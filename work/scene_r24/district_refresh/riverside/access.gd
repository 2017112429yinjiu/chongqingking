extends "survey.gd"
## Four sector visits using inherited entrances, plus a closer road-line check.

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for plot: Dictionary in layout.plots:
		var id := int(plot.plot_id)
		if id not in [37, 42, 76]:
			continue
		var front := -float(plot.depth)*.5
		var door := float(plot.door_u)
		var points := []
		if id == 37:
			var foot := world(plot, door, front - float(plot.front_stair_m) - .55, 0)
			points = [public_floor([foot.x, -foot.z], plot.height),
				world(plot, door, front - .55, .06), world(plot, door, front + .72, .06)]
		else:
			points = [world(plot, door, front - .94, .072), world(plot, door, front + .75, .072),
				world(plot, door, -front + .79, .072)]
		await walk_pair("plot_%02d" % id, points)
	var centre := Array(preload("res://scripts/day_one.gd").YARD_PATH).slice(1, -1)
	await walk_pair("original_200", centre)
	var tea_street := []
	for point: Array in [[84, -233], [86, -227], [87, -221], [87, -214], [86, -208],
			[86.25063, -200.59331]]:
		tea_street.append(ground_point(point, .04))
	await walk_pair("tea_street_to_east_garden", tea_street)
	var trace: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/riverside.json"))
	for route: Dictionary in trace.routes:
		if route.id != "zhongxing_northeast":
			continue
		var points: Array[Vector3] = []
		for i in range(route.points.size() - 1):
			var a := Vector2(route.points[i][0], route.points[i][1])
			var b := Vector2(route.points[i + 1][0], route.points[i + 1][1])
			var steps := maxi(1, ceili(a.distance_to(b) / 8.0))
			for j in steps:
				var p := a.lerp(b, float(j) / float(steps))
				points.append(ground_point([p.x, p.y], .04))
		points.append(ground_point(route.points[-1], .04))
		await walk_pair("zhongxing_subdivided", points)
	FileAccess.open(output.path_join("access.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"walks": walks, "checks": checks, "outer": scene.scene_identity.get("district_500", {}),
	}, "  "))
	quit(2 if ever_failed else 0)
