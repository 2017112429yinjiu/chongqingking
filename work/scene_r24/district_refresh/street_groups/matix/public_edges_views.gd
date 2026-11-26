extends "../../riverside/survey.gd"
## Eye-height images at the measured service lane and the two road-edge contacts.

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	scene.hud.hide()
	root.use_occlusion_culling = false
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.fov = 69.0
	camera.far = 265.0
	camera.make_current()
	var points := [
		["service_lane", [116.0,213.84], [98.09,208.0], 1.63],
		["service_lane_return", [92.99,211.57], [105.3,209.37], 1.63],
		["zhongxing_east_kerb", [217.404,170.0], [216.2,178.3], .54],
	]
	var stations := []
	for point: Array in points:
		var eye := ground_point(point[1], float(point[3]))
		var aim := ground_point(point[2], 1.18)
		camera.global_position = eye
		camera.look_at(aim)
		await process_frame
		RenderingServer.force_draw(false, 1.0 / 60.0)
		var result := root.get_texture().get_image().save_png(output.path_join(point[0] + ".png"))
		assert(result == OK)
		stations.append({"id":point[0],"eye_xyz":[eye.x,eye.y,eye.z],"aim_xyz":[aim.x,aim.y,aim.z]})
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"renderer":RenderingServer.get_current_rendering_method(),"device":RenderingServer.get_video_adapter_name(),
		"scene":scene.scene_file_path,"size":str(root.size),"stations":stations,
	}, "  "))
	quit()
