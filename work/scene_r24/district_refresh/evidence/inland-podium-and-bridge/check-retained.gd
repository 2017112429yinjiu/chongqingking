extends "../../continuous_site_walk.gd"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var layout: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var explorer = scene.explorer
	for lane: Dictionary in layout.lanes:
		if lane.type != "street":
			continue
		var plot: Dictionary = layout.plots[lane.plots[0]]
		var id := int(plot.plot_id)
		if id not in [54, 56]:
			continue
		var entrance_y: float = plot.height
		var front_edge: float = -plot.depth * .5
		var approach: Array = lane.points.duplicate()
		approach.reverse()
		var route: Array[Vector3] = []
		for point: Array in approach:
			route.append(public_floor(point, entrance_y))
		for offset: float in [-.55, .72]:
			route.append(world(plot, plot.door_u, front_edge + offset, .06))
		if not check("street_origin_%02d" % id, not route.has(Vector3.INF), approach):
			continue
		explorer.begin_route_test(route[0], route[1])
		await frames(20)
		var start: Vector3 = explorer.body.global_position
		var there := await leg_without_placement("plot_%02d_entry" % id, route.slice(1))
		if there.pass:
			route.reverse()
			await leg_without_placement("plot_%02d_return" % id, route.slice(1))
			var delta: float = explorer.body.global_position.distance_to(start)
			check("same_start_on_return_%02d" % id, delta <= .46, delta)
		explorer.end_route_test()
	await check_shared_entrance(layout)
	var sections := {}
	var sites := {
		"10_side_street": [[231.14,137.45], [240.2,141.25], [243.34,148.15], [267.0,153.24]],
		"26_public_edge_and_neighbour": [[177.01,-123.16], [194.26,-128.16],
			[187.24,-140.98], [189.76,-174.2]],
		"54_and_56_road_layers": [[-135.13,-116.32], [-122.29,-134.60], [-131.20,-125.71],
			[-114.69,-130.14], [-107.35,-131.81], [-99.30,-133.84]],
	}
	for label: String in sites:
		var samples := []
		for en: Array in sites[label]:
			samples.append({"en": en, "layers": column(en)})
		sections[label] = samples
	var result := {
		"kind": "old prototype doorstep and immediately adjacent ground",
		"runtime": scene.scene_identity.district_500,
		"teleports_between_legs": 0,
		"walks": walks,
		"site_sections": sections,
		"checks": checks,
	}
	FileAccess.open(output.path_join("retained-entrances.json"), FileAccess.WRITE).store_string(
		JSON.stringify(result, "  "))
	quit(2 if ever_failed else 0)

func check_shared_entrance(layout: Dictionary) -> void:
	for lane: Dictionary in layout.lanes:
		if lane.type != "shared":
			continue
		var plot: Dictionary = layout.plots[lane.plots[0]]
		var neighbour: Dictionary = layout.plots[lane.plots[1]]
		if int(plot.plot_id) != 56 or int(neighbour.plot_id) != 54:
			continue
		var exit: Array = plot.court.exit_local
		var route: Array = [
			public_floor(lane.points[1], neighbour.height),
			public_floor(lane.points[0], plot.height),
			world(plot, exit[0] + 1.15, exit[1], .06),
		]
		if not check("shared_54_56_supported", not route.has(Vector3.INF), lane.points):
			return
		var explorer = scene.explorer
		explorer.begin_route_test(route[0], route[1])
		await frames(20)
		var start: Vector3 = explorer.body.global_position
		var there := await leg_without_placement("shared_54_to_56_courtyard", route.slice(1))
		if there.pass:
			route.reverse()
			await leg_without_placement("shared_56_to_54_return", route.slice(1))
			var delta: float = explorer.body.global_position.distance_to(start)
			check("shared_returned_to_54", delta <= .46, delta)
		explorer.end_route_test()
		return
