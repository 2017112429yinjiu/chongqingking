extends "../../riverside/survey.gd"

const WALL_NAME := "COL_Outer500_Retaining_and_boundaries"

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
	var wall := scene.find_child(WALL_NAME, true, false) as MeshInstance3D
	var finished := wall.mesh
	var old_layer := (load("res://assets/district_500/matix_streets.glb") as PackedScene).instantiate()
	var old_mesh := (old_layer.find_child(WALL_NAME, true, false) as MeshInstance3D).mesh
	old_layer.free()
	var eye := ground_point([214.8, 169.8], 1.27)
	var target := ground_point([213.5, 186.0], .88)
	wall.mesh = old_mesh
	await shot("uphill_before", eye, target)
	wall.mesh = finished
	await shot("uphill_after", eye, target)
	var reverse := ground_point([212.7, 186.4], 1.64)
	await shot("downhill_after", reverse, ground_point([214.4, 168.0], 1.02))
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"eye": [eye.x,eye.y,eye.z], "target": [target.x,target.y,target.z], "reverse": [reverse.x,reverse.y,reverse.z],
		"release": scene.scene_identity.get("district_500", {}), "renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name()},"  "))
	quit()
