extends "../survey.gd"

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
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/layout.json"))
	var control := Node3D.new()
	scene.get_node("City").add_child(control)
	var original: Dictionary = data.outer_canopy[527]
	var clusters = preload("res://scripts/district_r21.gd").install_canopy(control, [original], data.canopy_pivots, 62.0)
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.fov = 67.0
	camera.far = 190.0
	var eye := ground_point([-104, -231.5], 1.63)
	var target := ground_point([-130, -226.6], .55)
	camera.global_position = eye
	camera.look_at(target)
	camera.make_current()
	for before: bool in [true, false]:
		control.visible = before
		await process_frame
		RenderingServer.force_draw(false,1.0/60.0)
		var path := output.path_join("lower_return_" + ("before" if before else "after") + ".png")
		assert(root.get_texture().get_image().save_png(path) == OK)
	FileAccess.open(output.path_join("tree-view.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"eye": [eye.x,eye.y,eye.z], "target": [target.x,target.y,target.z], "donor": original,
		"control_clusters": clusters, "renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name()}, "  "))
	quit()
