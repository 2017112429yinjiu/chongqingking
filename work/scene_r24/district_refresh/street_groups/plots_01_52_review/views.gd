extends "../../continuous_site_walk.gd"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name()!="headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	scene.hud.hide()
	var matrices := ""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--site-fixed-views="):
			matrices=arg.trim_prefix("--site-fixed-views=")
	if not check("native_comparison",graphics and not matrices.is_empty(),matrices):
		quit(2)
		return
	var views: Array = JSON.parse_string(FileAccess.get_file_as_string(matrices))
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.make_current()
	var records := []
	for row: Dictionary in views:
		camera.global_position = point(row.eye_enu)
		camera.look_at(point(row.target_enu))
		camera.fov = row.fov_deg
		await process_frame
		RenderingServer.force_draw(false,1.0/60.0)
		var image := root.get_texture().get_image()
		var save := image.save_png(output.path_join(row.file))
		check("native_png_"+str(row.file),save==OK,save)
		var view := camera.get_camera_transform().affine_inverse()
		var projection := camera.get_camera_projection()
		records.append({"shot":row,"view_columns":[triple(view.basis.x,0.),triple(view.basis.y,0.),
			triple(view.basis.z,0.),triple(view.origin,1.)],
			"projection_columns":[quad(projection.x),quad(projection.y),quad(projection.z),quad(projection.w)],
			"pixels":[image.get_width(),image.get_height()],"png_write_code":save})
	FileAccess.open(output.path_join("matrices.json"),FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	quit(2 if ever_failed else 0)

func point(row: Array) -> Vector3:
	return Vector3(row[0],row[2],-row[1])

func triple(v: Vector3,last: float) -> Array:
	return [v.x,v.y,v.z,last]

func quad(v: Vector4) -> Array:
	return [v.x,v.y,v.z,v.w]
