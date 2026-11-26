extends "../measure.gd"

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
	var stations := [
		["matix_liangtingzi_join", [52.5, 147.2], [65.0, 140.8]],
		["liangtingzi_43", [102.0, 154.2], [115.0, 162.3]],
		["liangtingzi_43_reverse", [116.1, 162.8], [105.0, 156.2]],
	]
	var cameras := []
	for station: Array in stations:
		var eye := ground_point(station[1], 1.64)
		var target := ground_point(station[2], 1.35)
		await shot(station[0], eye, target)
		cameras.append({"id": station[0], "eye": [eye.x, eye.y, eye.z],
			"target": [target.x, target.y, target.z]})
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"cameras": cameras, "scene": scene.scene_identity.get("district_500", {}),
		"renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name()}, "  "))
	quit()
