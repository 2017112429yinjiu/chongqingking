extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(24)
	await trial("northwest_up",[terrain([-179.505,121.3877]),terrain([-184.9709,127.5952])],false)
	await trial("two_entrances",[terrain([228.83,134.2]),terrain([228.4311,144.7380])],false)
	FileAccess.open(output.path_join("probe.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
