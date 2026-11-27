extends "../../continuous_site_walk.gd"

func verification_site() -> Dictionary:
	return {
		"resource":"res://assets/district_500/liangtingzi-45-46.json",
		"surfaces":{"45":"COL_Liangtingzi45_PublicFlags", "46":"COL_Liangtingzi46_PublicDescent"},
	}

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name() != "headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	if graphics:
		scene.hud.hide()
		for arg in OS.get_cmdline_user_args():
			if arg.begins_with("--site-fixed-views="):
				await site_fixed_frames(arg.trim_prefix("--site-fixed-views="))
	var spec := verification_site()
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(spec.resource))
	var path: String = get_script().resource_path.get_base_dir().path_join("field.json")
	var field: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var reports := {}
	var actor = scene.explorer
	var plots: Array = [] if "--site-view-only" in OS.get_cmdline_user_args() else spec.surfaces.keys()
	for id: String in plots:
		var route: Array[Vector3] = []
		var sections := []
		var support_count := 0
		for row: Array in plan.walks[id]:
			route.append(Vector3(row[0],row[2],-row[1]))
			var layers := column(row.slice(0,2))
			sections.append({"enu":row,"hits":layers})
			for layer: Array in layers:
				if layer[0] == spec.surfaces[id] and absf(layer[1]-row[2]) < .075 and layer[2] > .83:
					support_count += 1
		check("public_support_"+id,support_count==route.size(),support_count)
		var contact := preload("res://scripts/build_collisions.gd").raycast_ground(scene,route[0]+Vector3.UP*.54,1.2)
		if not check("street_origin_"+id,not contact.is_empty(),enu(route[0])): continue
		actor.set_walk_origin(contact.position+Vector3.UP*.035,route[1]+Vector3.UP)
		await frames(16)
		var start: Vector3 = actor.body.global_position
		var outward := await leg_without_placement(id+"_public_out",route.slice(1))
		var end: Vector3 = actor.body.global_position
		var en := Vector2(end.x,-end.z)
		var old: Array = field.old_plots[id].outline_en
		var gap := INF
		for i in old.size():
			var a := Vector2(old[i][0],old[i][1])
			var next: Array = old[(i+1)%old.size()]
			var b := Vector2(next[0],next[1])
			gap = minf(gap,en.distance_to(Geometry2D.get_closest_point_to_segment(en,a,b)))
		var back := {}
		if outward.pass:
			check("at_public_turn_"+id,end.distance_to(route[-1]) < .41,enu(end))
			if graphics:
				actor.aim_route_test(route[-2])
				await eye_frame(id+"-player-turn",null)
			route.reverse()
			back = await leg_without_placement(id+"_public_return",route.slice(1))
			check("same_street_"+id,actor.body.global_position.distance_to(start)<.48,enu(actor.body.global_position))
		actor.end_route_test()
		reports[id] = {"out":outward,"back":back,"start_enu":enu(start),"turn_enu":enu(end),
			"old_outline_edge_distance_m":gap,"sections":sections,"scope":"public street and outdoor path"}
	FileAccess.open(output.path_join("round-trip.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"engine":Engine.get_version_info().string,"renderer":RenderingServer.get_current_rendering_method(),
		"identity":scene.scene_identity.district_500,"reports":reports,"traces":walks,"checks":checks,
		"teleports_between_legs":0,"native_frames":view_positions},"  "))
	quit(2 if ever_failed else 0)
