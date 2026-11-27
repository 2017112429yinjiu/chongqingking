extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/north-38-40-41.json"

func en2(p: Array) -> Vector2:
	return Vector2(p[0],p[1])

func en3(p: Array) -> Vector3:
	return Vector3(p[0],p[2],-p[1])

func photo_args() -> String:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--site-fixed-views="):
			return arg.trim_prefix("--site-fixed-views=")
	return ""

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	graphics=DisplayServer.get_name()!="headless"
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var field_path: String = get_script().resource_path.get_base_dir().path_join("field.json")
	var field: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(field_path))
	var actor = scene.explorer
	if graphics:
		scene.hud.hide()
		if not photo_args().is_empty():
			await site_fixed_frames(photo_args())
	var results := {}
	var plots := [] if "--site-view-only" in OS.get_cmdline_user_args() else ["38","40","41"]
	for plot: String in plots:
		var rows: Array=plan.walks[plot]
		var route: Array[Vector3]=[]
		for row in rows:
			route.append(en3(row))
		var start := route[0]
		var support := preload("res://scripts/build_collisions.gd").raycast_ground(scene,start+Vector3.UP*.8,2.4)
		if not check("street_origin_"+plot,not support.is_empty(),enu(start)):
			continue
		actor.set_walk_origin(support.position+Vector3.UP*.035,route[1]+Vector3.UP)
		await frames(15)
		var initial: Vector3=actor.body.global_position
		var out := await leg_without_placement("north_"+plot+"_out",route.slice(1))
		var turn: Vector3=actor.body.global_position
		var p:=Vector2(turn.x,-turn.z)
		var old_shape:=PackedVector2Array()
		for point: Array in field.old_plots[plot].outline_en:
			old_shape.append(en2(point))
		var distance := INF
		for i in old_shape.size():
			var on_edge:=Geometry2D.get_closest_point_to_segment(p,old_shape[i],old_shape[(i+1)%old_shape.size()])
			distance=minf(distance,p.distance_to(on_edge))
		var back := {}
		if out.pass:
			check("turn_on_public_floor_"+plot,absf(turn.y-route[-1].y)<.22,
				{"turn_enu":enu(turn),"route_y":route[-1].y})
			if graphics:
				actor.aim_route_test(route[-2])
				await eye_frame(plot+"-player-turn",null)
			route.reverse()
			back=await leg_without_placement("north_"+plot+"_back",route.slice(1))
			check("returned_to_public_start_"+plot,actor.body.global_position.distance_to(initial)<.47,enu(actor.body.global_position))
		actor.end_route_test()
		results[plot]={"start_enu":enu(initial),"turn_enu":enu(turn),"old_footprint_edge_distance_m":distance,
			"turn_inside_old_outline":Geometry2D.is_point_in_polygon(p,old_shape),
			"height_above_old_trial_floor_m":turn.y-field.old_plots[plot].floor_y,
			"public_scope":"street margin", "out":out,"back":back}
	FileAccess.open(output.path_join("round-trip.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"engine":Engine.get_version_info().string,"identity":scene.scene_identity.district_500,
		"renderer":RenderingServer.get_current_rendering_method(),"trips":results,"traces":walks,"checks":checks,"native_frames":view_positions,
		"teleports_between_legs":0},"  "))
	quit(2 if ever_failed else 0)
