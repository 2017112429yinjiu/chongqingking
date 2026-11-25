extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(24)
	var geo: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://source_data/geo_layout.json"))
	for way: Dictionary in geo.paths:
		if int(way.id)!=734116601:continue
		var points: Array=[]
		for q: Array in way.points.slice(0,47):points.append(terrain(q)+Vector3.UP*.045)
		await trial("osm_734116601",points)
	FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
