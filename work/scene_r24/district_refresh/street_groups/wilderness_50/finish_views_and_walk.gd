extends "walk.gd"

func eye_frame(label: String, focus: Variant) -> void:
	if label=="street":
		var data := ""
		for arg in OS.get_cmdline_user_args():
			if arg.begins_with("--fixed-views="):
				data = arg.trim_prefix("--fixed-views=")
		var views: Array=JSON.parse_string(FileAccess.get_file_as_string(data))
		var fixed := Camera3D.new()
		scene.add_child(fixed)
		fixed.make_current()
		var report := []
		for spec: Dictionary in views:
			var p: Array=spec.eye_enu
			var aim: Array=spec.target_enu
			fixed.global_position=Vector3(p[0],p[2],-p[1])
			fixed.look_at(Vector3(aim[0],aim[2],-aim[1]))
			fixed.fov=spec.fov_deg
			await process_frame
			RenderingServer.force_draw(false,1.0/60.0)
			var img := root.get_texture().get_image()
			var code := img.save_png(output.path_join(spec.file))
			report.append({"frame":spec,"save_code":code,"pixels":[img.get_width(),img.get_height()]})
			check("native_"+spec.file,code==OK,spec.eye_enu)
		FileAccess.open(output.path_join("fixed-views.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
		scene.explorer.camera.make_current()
		fixed.queue_free()
	await super.eye_frame(label,focus)
