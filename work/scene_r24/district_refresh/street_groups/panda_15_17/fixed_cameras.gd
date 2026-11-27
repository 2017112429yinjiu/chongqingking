extends "res://../../scene_r24/day_one/verify.gd"

func enu(point: Array) -> Vector3:
	return Vector3(point[0], point[2], -point[1])

func verify() -> void:
	RenderingServer.render_loop_enabled = false
	output = preload("res://scripts/qa_context.gd").directory()
	scene = load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	var input: String
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--a2-views="):
			input = arg.trim_prefix("--a2-views=")
	var views: Array = JSON.parse_string(FileAccess.get_file_as_string(input))
	var camera := Camera3D.new()
	camera.cull_mask &= ~int(scene.explorer.FIRST_PERSON_BODY_LAYER)
	scene.add_child(camera)
	camera.make_current()
	var checks := []
	for frame: Dictionary in views:
		camera.global_position = enu(frame.eye_enu)
		camera.look_at(enu(frame.target_enu))
		camera.fov = frame.fov_deg
		await process_frame
		RenderingServer.force_draw(false, 1.0 / 60.0)
		var image := root.get_texture().get_image()
		var saved := image.save_png(output.path_join(frame.file))
		checks.append({"frame":frame,"save_code":saved,"pixels":[image.get_width(),image.get_height()]})
		print("A2_FIXED_FRAME ", frame.file, " ", saved)
	FileAccess.open(output.path_join("views.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(0 if checks.all(func(row: Dictionary) -> bool: return row.save_code==OK) else 2)
