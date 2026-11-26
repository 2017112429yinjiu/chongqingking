extends "../../riverside/survey.gd"
## Walk from the mapped street shoulder to the podium and back, then compare those eye positions.

const PLAN := "res://assets/district_500/xingchen.json"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var route: Array[Vector3] = []
	var sections := []
	for station: Array in plan.game_approach_east_north:
		route.append(ground_point(station,.043))
		sections.append({"east_north":station,"layers":column(station)})
	var out := {"scene":scene.scene_file_path,"renderer":RenderingServer.get_current_rendering_method(),
		"adapter":RenderingServer.get_video_adapter_name(),"sections":sections,
		"district":scene.scene_identity.district_500}
	if DisplayServer.get_name() == "headless":
		await walk_pair("jiefang_west_830761786_to_xingchen_27",route)
		out["walks"] = walks
		out["checks"] = checks
	else:
		out["view_stations"] = await views()
	FileAccess.open(output.path_join("xingchen.json"),FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	quit(2 if ever_failed else 0)

func views() -> Array:
	scene.hud.hide()
	root.use_occlusion_culling = false
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.fov = 72.0
	camera.far = 285.0
	camera.make_current()
	var stations := []
	var points := [
		["jiefang_approach", [191.0,-130.0],[205.0,-151.5],10.0],
		["front_eye_height", [203.8,-138.8],[196.0,-150.0],9.0],
		["east_look_back", [219.0,-140.9],[198.3,-152.4],11.0],
		["tower_from_west", [148.5,-144.0],[189.0,-159.0],38.0],
	]
	for point: Array in points:
		var eye := ground_point(point[1],1.64)
		var target := ground_point(point[2],float(point[3]))
		camera.global_position = eye
		camera.look_at(target)
		await process_frame
		RenderingServer.force_draw(false,1.0/60.0)
		var result := root.get_texture().get_image().save_png(output.path_join(point[0]+".png"))
		assert(result == OK)
		stations.append({"id":point[0],"eye_xyz":[eye.x,eye.y,eye.z],"target_xyz":[target.x,target.y,target.z]})
	return stations
