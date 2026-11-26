extends "../../riverside/survey.gd"

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
	var args := OS.get_cmdline_user_args()
	var skyline := ["tower_silhouette",Vector3(193,61.,-67.),Vector3(190,106.,72.)]
	var cameras := [
		["factory_return",ground_point([244.066101,-127.010689],1.64),Vector3(226.5,13.9,115.)],
		["factory_window",ground_point([234.7,-124.3],1.61),Vector3(233.7,13.3,119.5)],
		skyline,
	]
	if "--qa-skyline-only" in args:
		cameras = [skyline]
	elif not "--qa-without-guoco" in args:
		cameras.append(["podium_underpass",ground_point([192,-88],1.63),Vector3(192,21.4,66)])
	for row: Array in cameras:
		await shot(row[0],row[1],row[2])
	var positions := []
	for row: Array in cameras:
		positions.append({"id":row[0],"eye":[row[1].x,row[1].y,row[1].z],"target":[row[2].x,row[2].y,row[2].z]})
	FileAccess.open(output.path_join("cameras.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"views":positions,"renderer":RenderingServer.get_current_rendering_method(),
		"adapter":RenderingServer.get_video_adapter_name(),"scene":scene.scene_file_path},"  "))
	quit()
