extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/zhongxing-arcade10.json"
const FLOOR := "COL_Zhongxing10_ArcadePublicFlags"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name() != "headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var parent := "--qa-without-zhongxing10-arcade" in OS.get_cmdline_user_args()
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var route: Array[Vector3] = []
	var sections := []
	var actor = scene.explorer
	for mark: Array in plan.walks["10"]:
		var point := Vector3(mark[0], mark[2], -mark[1])
		route.append(point)
		sections.append({"route_enu": mark, "hits": column(mark.slice(0,2))})
	check("arcade_layer_presence", (scene.find_child("ZhongxingArcade10",true,false) != null) != parent)
	if parent:
		var ground := preload("res://scripts/build_collisions.gd").raycast_ground(scene,route[0]+Vector3.UP*.65,2.)
		check("parent_has_start_floor", not ground.is_empty(), enu(route[0]))
		if not ground.is_empty():
			actor.set_walk_origin(ground.position+Vector3.UP*.035,route[1])
			await frames(16)
	else:
		check("street_spawn", actor.walking and actor.body.is_on_floor()
			and actor.body.global_position.distance_to(route[0])<.17, enu(actor.body.global_position))
		var stable := sections.filter(func(row: Dictionary) -> bool:
			return row.hits.any(func(hit: Array) -> bool:
				return hit[0] == FLOOR and absf(hit[1] - row.route_enu[2]) < .045 and hit[2]>.91))
		check("registered_supports", stable.size() == route.size(), stable.size())

	if graphics:
		scene.hud.hide()
		await eye_frame("street-at-the-new-curb", [plan.walks["10"][3][0],plan.walks["10"][3][1],route[3].y+1.50])
	var start: Vector3 = actor.body.global_position
	var result := await leg_without_placement("street_to_public_arcade",route.slice(1))
	if result.pass:
		check("public_arcade_turn", actor.body.global_position.distance_to(route[-1]) < .38, enu(actor.body.global_position))
		if graphics:
			actor.aim_route_test(route[-3])
			await eye_frame("under-the-eaves-look-back", null)
		route.reverse()
		await leg_without_placement("arcade_back_to_the_same_street",route.slice(1))
		check("same_street_point", actor.body.global_position.distance_to(start)<.44, enu(actor.body.global_position))
		if graphics:
			await eye_frame("returned-to-the-street", null)
	actor.end_route_test()
	var ray_results := []
	var controls: String = ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--arcade-camera-plan="):
			controls = arg.trim_prefix("--arcade-camera-plan=")
	if not controls.is_empty():
		var views: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(controls))
		var end_a: Array = plan.pillar_caps_en[0]
		var end_b: Array = plan.pillar_caps_en[1]
		var final_point := Vector3((end_a[0]+end_b[0])*.5, 50.28, -(end_a[1]+end_b[1])*.5)
		for v: Dictionary in views.views.slice(0,3):
			var eye: Array = v.eye_enu
			var from := Vector3(eye[0],eye[2],-eye[1])
			var ray := PhysicsRayQueryParameters3D.create(from,final_point,1)
			ray.hit_back_faces = true
			var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
			ray_results.append({"id":v.id,"eye":eye,"target":enu(final_point),"hit":{} if hit.is_empty() else {
				"owner":String(hit.collider.get_parent().name),"point_enu":enu(hit.position)}})
	var identity: Dictionary = scene.scene_identity.district_500
	var report := {"parent": parent, "engine":Engine.get_version_info().string,"runtime": identity,
		"checks": checks,"sections":sections, "walks":walks, "sightlines":ray_results,
		"native_frames": view_positions,"resets_between_legs":0}
	FileAccess.open(output.path_join("round-trip.json"),FileAccess.WRITE).store_string(JSON.stringify(report, "  "))
	quit(2 if ever_failed else 0)
