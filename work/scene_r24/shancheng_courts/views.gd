extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	scene.hud.hide()
	# All heights are fixed between captures, including frames taken before construction.
	for view: Array in [
		["from_pickup", Vector3(-119.8, 15.9, 26.8), Vector3(-149.4, 24.6, -13.5)],
		["lane_front", Vector3(-140.3, 19.7, -7.8), Vector3(-158.0, 23.5, -21.4)],
		["school_entry", Vector3(-138.6, 23.4, -36.1), Vector3(-133.1, 25.8, -47.)],
		["school_door_detail",Vector3(-139.60,23.60,-41.74),Vector3(-134.70,25.0,-46.20)],
		["school_seating",Vector3(-131.63,23.0,-39.28),Vector3(-126.29,23.60,-39.87)],
		["long_hall", Vector3(-163.2, 21.22, -30.8), Vector3(-169.2, 22.0, -31.8)],
		["reading_room",Vector3(-132.2,28.06,-53.1),Vector3(-123.1,28.18,-55.5)],
		["upper_court", Vector3(-157.0, 22.6, -39.5), Vector3(-132.0, 25.0, -49.0)],
	]:
		await shot(view[0], view[1], view[2])
	quit()
