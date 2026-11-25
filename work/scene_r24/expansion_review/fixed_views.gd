extends "../../scene_r24/day_one/verify.gd"
## Shared cameras for the original district and its 500 m trial.
func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	for i in 1800:
		if scene.get("gameplay") != null:
			break
		await physics_frame
	if not check("first_shift_loaded", scene.get("gameplay") != null):
		quit(2)
		return
	await frames(25)
	# Model provided for internal registration only. Compare the distributable street layers.
	var registration := scene.find_child("LocalCityFrame", true, false) as Node3D
	if registration:
		registration.hide()
	var camera := Camera3D.new()
	camera.fov = 66
	camera.far = 1500
	scene.add_child(camera)
	camera.current = true
	var stations := [
		["service_front", Vector3(-6.82,23.98,-12.58), Vector3(3.9,23.38,-12.50)],
		["west", Vector3(-92.22,9.18,74.53), Vector3(-119.27,8.4,67.29)],
		["east", Vector3(93.89,16.91,48.88), Vector3(115.26,18.4,30.86)],
		["north", Vector3(-30.26,35.09,-93.24), Vector3(-46.3,37.2,-116.17)],
		["south", Vector3(41.95,8.9,92.18), Vector3(47.5,6.7,119.62)],
		["oblique", Vector3(282,271,368), Vector3(0,10,0)],
		["plan", Vector3(0,530,0), Vector3(0,0,0)]
	]
	var records := []
	for station: Array in stations:
		var plan: bool = station[0] == "plan"
		camera.projection = Camera3D.PROJECTION_ORTHOGONAL if plan else Camera3D.PROJECTION_PERSPECTIVE
		camera.size = 540
		camera.global_position = station[1]
		camera.look_at(station[2], Vector3.FORWARD if plan else Vector3.UP)
		camera.current = true
		await frames(6)
		RenderingServer.force_draw(false, 1.0/60.0)
		await capture(station[0])
		records.append({"site":station[0], "camera":str(station[1]), "target":str(station[2])})
	var record := {"entry":"res://first_shift.tscn","checks":checks,"views":records,"local_registration_model_visible":false,"device":RenderingServer.get_video_adapter_name(),"viewport":str(root.size)}
	FileAccess.open(output.path_join("cameras.json"),FileAccess.WRITE).store_string(JSON.stringify(record,"  "))
	quit(2 if ever_failed else 0)
