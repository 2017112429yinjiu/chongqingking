extends "../measure.gd"

const MATIX_SITE := "res://assets/district_500/matix_streets.json"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATIX_SITE))
	for lane: Dictionary in layout.lanes:
		if lane.type != "street":
			continue
		var plot: Dictionary = layout.plots[lane.plots[0]]
		if int(plot.plot_id) != 43:
			continue
		var alignment: Array = lane.points.duplicate()
		alignment.reverse()
		var path: Array[Vector3] = []
		for point: Array in alignment:
			path.append(public_floor(point, plot.height))
		var front: float = -plot.depth * .5
		path.append(world(plot, plot.door_u, front - .55, .06))
		path.append(world(plot, plot.door_u, front + .72, .06))
		assert(not path.has(Vector3.INF))
		await walk_pair("street_43", path)
		break
	assert(checks.size() == 2)
	var rear: Array[Vector3] = []
	for point: Array in plan.rear_stair.path_east_north_up:
		rear.append(Vector3(point[0], point[2] + .045, -point[1]))
	await walk_pair("rear_stair_43", rear)
	FileAccess.open(output.path_join("approaches.json"), FileAccess.WRITE).store_string(JSON.stringify(checks, "  "))
	quit(2 if ever_failed else 0)
