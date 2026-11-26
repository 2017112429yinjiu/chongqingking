extends "../../outer_neighborhood/survey.gd"
## Compare the same shoreline stations using physical contacts and the player controller.

var walks := []

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	if "--capture-riverside" in OS.get_cmdline_user_args():
		await capture_bank()
		quit()
		return
	var plan_file := OS.get_environment("CQ_RIVER_PLAN")
	if plan_file.is_empty():
		plan_file = "res://assets/district_500/riverside.json"
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(plan_file))
	var sections := {}
	for route: Dictionary in plan.routes:
		var points: Array[Vector3] = []
		var samples := []
		for xy: Array in route.points:
			var layers := column(xy)
			var terrain := layers.filter(func(hit: Array) -> bool:
				return String(hit[0]).begins_with("COL_Outer500_Surface_"))
			if not terrain.is_empty():
				points.append(Vector3(xy[0], terrain[0][1] + 0.04, -xy[1]))
			samples.append({"east_north": xy, "layers": layers})
		sections[route.id] = samples
		if "--survey-only" in OS.get_cmdline_user_args():
			continue
		if points.size() != route.points.size():
			check(route.id, false, {"unsupported_stations": route.points.size() - points.size()})
			continue
		await walk_pair(route.id, points)
	var plot_columns := {}
	for plot: Dictionary in plan.plots:
		plot_columns[str(int(plot.id))] = column(plot.east_north)
	FileAccess.open(output.path_join("riverside.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"engine": Engine.get_version_info().string, "scene": scene.scene_file_path,
		"outer": scene.scene_identity.get("district_500", {}), "sections": sections,
		"plots": plot_columns, "walks": walks, "checks": checks,
	}, "  "))
	quit(2 if ever_failed else 0)

func walk_pair(id: String, points: Array) -> void:
	for back: bool in [false, true]:
		var label := id + ("_back" if back else "_out")
		scene.explorer.begin_route_test(points[0], points[1])
		await frames(20)
		var stride := []
		var sample := func() -> void:
			if Engine.get_physics_frames() % 15 == 0:
				var p: Vector3 = scene.explorer.body.global_position
				stride.append([p.x, p.y, -p.z])
		physics_frame.connect(sample)
		var result := await WalkTest._walk(scene, points.slice(1), label)
		physics_frame.disconnect(sample)
		check(label, result["pass"], result)
		walks.append({"id": label, "checks": result, "samples_east_up_north": stride})
		points.reverse()

func capture_bank() -> void:
	var layer := scene.find_child("RiversideWalk", true, false) as Node3D
	assert(layer != null)
	scene.hud.hide()
	root.use_occlusion_culling = false
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.far = 190.0
	camera.fov = 67
	camera.make_current()
	var stations := [
		["lower_west", [-194, -213], [-164, -219]],
		["lower_return", [-104, -231.5], [-130, -226.6]],
		["park_front", [-159, -197.2], [-131, -199.4]],
		["garden_east", [65, -232], [93, -234]],
		["west_connector", [-201, -204], [-207, -213]],
	]
	var cameras := []
	for station: Array in stations:
		var eye := ground_point(station[1], 1.63)
		var target := ground_point(station[2], .55)
		camera.global_position = eye
		camera.look_at(target)
		cameras.append({"name": station[0], "eye": [eye.x, eye.y, eye.z], "target": [target.x, target.y, target.z]})
		for enabled: bool in [false, true]:
			layer.visible = enabled
			await process_frame
			RenderingServer.force_draw(false, 1.0/60.0)
			var path: String = output.path_join(station[0] + ("_after.jpg" if enabled else "_before.jpg"))
			var result := root.get_texture().get_image().save_jpg(path, .91)
			assert(result == OK, path)
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"stations": cameras, "device": RenderingServer.get_video_adapter_name(),
		"renderer": RenderingServer.get_current_rendering_method(), "viewport": str(root.size),
		"riverside": scene.scene_identity.get("district_500", {}),
	}, "  "))

func ground_point(xy: Array, offset: float) -> Vector3:
	for layer: Array in column(xy):
		if String(layer[0]).begins_with("COL_Outer500_Surface_"):
			return Vector3(xy[0], layer[1] + offset, -xy[1])
	assert(false, str(xy))
	return Vector3.ZERO

func column(xy: Array) -> Array:
	var space := scene.get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(
		Vector3(xy[0], 130, -xy[1]), Vector3(xy[0], -28, -xy[1]), 1)
	var omitted: Array[RID] = []
	var layers := []
	for step in 14:
		var hit := space.intersect_ray(query)
		if hit.is_empty():
			break
		layers.append([String(hit.collider.get_parent().name), snappedf(hit.position.y, .001),
			snappedf(hit.normal.y, .001)])
		omitted.append(hit.rid)
		query.exclude = omitted
	return layers
