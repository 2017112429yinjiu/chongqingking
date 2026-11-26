extends "../riverside/survey.gd"

const PLANS := "res://assets/district_500/match_factory.json"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	var pictures := "--capture-factory" in OS.get_cmdline_user_args()
	if pictures:
		RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLANS))
	if pictures:
		await capture_factory(plan.walks_east_north)
		quit()
		return
	var tested := {}
	for route: String in plan.walks_east_north:
		var path: Array[Vector3] = []
		var profiles := []
		for point: Array in plan.walks_east_north[route]:
			profiles.append({"point": point, "hits": column(point)})
			path.append(ground_point(point, .045))
		tested[route] = profiles
		await walk_pair(route, path)
	var found := scene.find_child("COL_Guoco_MatchFactory_704006706", true, false)
	if not "--qa-without-match-factory" in OS.get_cmdline_user_args():
		check("factory_collider", found != null and found.has_node("CQ_StaticCollision"))
		for name: String in plan.retired_objects:
			check("retired_" + name, scene.find_child(name, true, false) == null)
	var file := FileAccess.open(output.path_join("factory_walks.json"), FileAccess.WRITE)
	assert(file)
	file.store_string(JSON.stringify({"profiles": tested, "walks": walks, "checks": checks,
		"outer": scene.scene_identity.get("district_500", {})}, "  "))
	quit(2 if ever_failed else 0)

func capture_factory(walks_en: Dictionary) -> void:
	scene.hud.hide()
	root.use_occlusion_culling = false
	var stations := [
		["lower_wall", [219.0, -124.0], Vector3(237.3, 15.1, 119.8)],
		["west_corner", [209.7, -117.8], Vector3(224.0, 14.5, 110.0)],
		["return", walks_en.lower_frontage[-1], Vector3(226.5, 13.9, 115.0)],
		["upper_wall", walks_en.uphill_wall[1], Vector3(244.0, 16.1, 107.0)],
	]
	var views := []
	for row: Array in stations:
		if "--factory-review-frames" in OS.get_cmdline_user_args() and row[0] not in ["lower_wall", "return"]:
			continue
		var eye := ground_point(row[1], 1.64)
		await shot(row[0], eye, row[2])
		views.append({"id": row[0], "eye": [eye.x,eye.y,eye.z], "target": [row[2].x,row[2].y,row[2].z]})
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"views": views, "renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name()}, "  "))
