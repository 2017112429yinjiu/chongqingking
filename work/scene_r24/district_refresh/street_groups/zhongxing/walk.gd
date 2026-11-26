extends "../../riverside/survey.gd"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/riverside.json"))
	for route: Dictionary in plan.routes:
		if route.id != "zhongxing_northeast":
			continue
		var major: Array[Vector3] = []
		for station: Array in route.points:
			major.append(ground_point(station, .04))
		await walk_pair("zhongxing_northeast", major)
		var detail: Array[Vector3] = []
		for i in range(route.points.size() - 1):
			var a := Vector2(route.points[i][0], route.points[i][1])
			var b := Vector2(route.points[i + 1][0], route.points[i + 1][1])
			var steps := maxi(1, ceili(a.distance_to(b) / 8.0))
			for j in steps:
				var p := a.lerp(b, float(j) / float(steps))
				detail.append(ground_point([p.x, p.y], .04))
		detail.append(ground_point(route.points[-1], .04))
		await walk_pair("zhongxing_subdivided", detail)
	FileAccess.open(output.path_join("zhongxing.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"scene": scene.scene_file_path, "renderer": RenderingServer.get_current_rendering_method(),
		"walks": walks, "checks": checks},"  "))
	quit(2 if ever_failed else 0)
