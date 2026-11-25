extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(24)
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for p: Dictionary in layout.plots:
		for side: String in p.get("kerb_stairs",{}):
			var stair: Dictionary=p.kerb_stairs[side]
			var dir:= -1. if side=="front" else 1.
			var low:=world(p,stair.toe[0]+stair.direction*.34,stair.toe[1],0)
			var hit:=public_floor([low.x,-low.z],p.height+.15)
			var route: Array=[hit,world(p,stair.pad[0],stair.pad[1],.05),world(p,p.door_u,stair.edge-dir*.7,.06)]
			await trial("%d_%s"%[p.plot_id,side],route)
	FileAccess.open(output.path_join("stairs.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
