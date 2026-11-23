extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	scene.hud.hide()
	for site:String in ["unit22_court","unit22_landing","unit22_gallery"]:
		scene.explorer.go_to_view(site)
		var cam:Camera3D=scene.explorer.camera
		cam.force_update_transform()
		await process_frame
		RenderingServer.camera_set_transform(cam.get_camera_rid(),cam.global_transform)
		await capture(site)
	quit(2 if ever_failed else 0)
