extends "../continuous_site_walk.gd"

const Collision := preload("res://scripts/build_collisions.gd")

func at(row: Array) -> Vector3:
	return Vector3(row[0], row[2], -row[1])

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	var source := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--acceptance-routes="):
			source = arg.trim_prefix("--acceptance-routes=")
	if source.is_empty() or not FileAccess.file_exists(source):
		push_error("An acceptance route file is required")
		quit(2)
		return
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source))
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var actor = scene.explorer
	var install: Dictionary = scene.scene_identity.district_500.acceptance
	for region: String in plan.get("regions", []):
		check("loaded_" + region, install.has(region), install.get(region, ""))
	var reports := {}
	for test: Dictionary in plan.routes:
		var route: Array[Vector3] = []
		for station: Array in test.stations:
			route.append(at(station))
		var start := Collision.raycast_ground(scene, route[0] + Vector3.UP * .5, 1.6)
		var name: String = test.id
		if not check(name + "_ground", not start.is_empty() and absf(start.position.y - route[0].y) < .38):
			continue
		actor.set_walk_origin(start.position + Vector3.UP * .035, route[1])
		await frames(16)
		var origin: Vector3 = actor.body.global_position
		var forward := await leg_without_placement(name + "_out", route.slice(1))
		var turn: Vector3 = actor.body.global_position
		var back := {}
		if forward.pass:
			check(name + "_destination_level", absf(turn.y - route[-1].y) < .45, enu(turn))
			route.reverse()
			back = await leg_without_placement(name + "_back", route.slice(1))
			check(name + "_return_root", actor.body.global_position.distance_to(origin) < .5,
				enu(actor.body.global_position))
		actor.end_route_test()
		reports[name] = {"out": forward, "back": back, "origin_enu": enu(origin), "end_enu": enu(turn),
			"teleports_between_legs": 0}
	FileAccess.open(output.path_join("acceptance-walks.json"), FileAccess.WRITE).store_string(JSON.stringify(
		{"scene": scene.scene_file_path, "engine": Engine.get_version_info().string, "active_regions": install,
		"reports": reports, "checks": checks, "traces": walks}, "  "))
	quit(2 if ever_failed else 0)
