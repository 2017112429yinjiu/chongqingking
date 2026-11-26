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
	var site: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/west-court.json"))
	var layer := scene.find_child("RiversideWestCourt", true, false) as Node3D
	var baseline := (load("res://assets/district_500/outer_district.glb") as PackedScene).instantiate()
	var street := (load("res://assets/district_500/matix_streets.glb") as PackedScene).instantiate()
	var active: Array[MeshInstance3D] = []
	var before: Array[Mesh] = []
	var after: Array[Mesh] = []
	for key: String in site.replacement_meshes:
		var mesh := scene.find_child(key, true, false) as MeshInstance3D
		active.append(mesh)
		var donor := street if key == "Outer500_Street_furniture" else baseline
		before.append((donor.find_child(key, true, false) as MeshInstance3D).mesh)
		after.append(mesh.mesh)
	baseline.free()
	street.free()
	var eye := ground_point([-136.7, -201.64], 1.63)
	var target := Vector3(-145.7, -5.30, 184.0)
	var reverse := Vector3(-148.6, -4.20, 181.0)
	layer.hide()
	for i in active.size():
		active[i].mesh = before[i]
	await shot("from_park_before", eye, target)
	layer.show()
	for i in active.size():
		active[i].mesh = after[i]
	await shot("from_park_after", eye, target)
	await shot("terrace_reverse", reverse, ground_point([-136.0, -200.9], 1.20))
	var west := ground_point([-158.9, -197.4], 1.35)
	await shot("stair_join", west, Vector3(-151.8, -5.32, 189.55))
	FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"eye": [eye.x, eye.y, eye.z], "target": [target.x, target.y, target.z], "reverse": [reverse.x, reverse.y, reverse.z],
		"adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(),
		"candidate": scene.scene_identity.district_500}, "  "))
	quit()
