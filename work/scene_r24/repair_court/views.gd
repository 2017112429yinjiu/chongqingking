extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	for v: Array in [
		["street", Vector3(-198.7,18.9,26.7), Vector3(-183.2,20.8,13.1)],
		["court", Vector3(-179.5,20.0,2.5), Vector3(-185.3,20.4,12.8)],
		["courtyard_entry", Vector3(-182.55,18.08,8.01), Vector3(-175.8,18.35,-1.9)],
		["workbench", Vector3(-187.22,18.03,14.34), Vector3(-182.7,17.81,16.25)],
		["street_eye", Vector3(-194.36,17.61,26.40), Vector3(-184.20,18.74,15.5)],
		["group", Vector3(-205,46,49), Vector3(-184,18,10)],
	]:
		await shot(v[0],v[1],v[2])
	quit()
