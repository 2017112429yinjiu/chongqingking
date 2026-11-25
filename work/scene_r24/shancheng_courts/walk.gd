extends "../../scene_r24/street_blocks/views.gd"

func level_point(xy: Array, height: float) -> Vector3:
	return Vector3(xy[0], height + .05, -xy[1])

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	var buildings: Dictionary = {}
	for building: Dictionary in data.buildings:
		buildings[building.id] = building
		var shell := scene.find_child("COL_Court_" + str(building.id), true, false)
		check(building.id+"_collisions", shell != null and not shell.find_children("*","StaticBody3D",true,false).is_empty())
	var rooms: Dictionary = {"renai":buildings.renai_long, "school":buildings.jinma_classrooms}
	for key: String in rooms:
		var rec: Dictionary = rooms[key]
		var pts: Array = []
		for q: Array in data.courtyard_connections[key]:
			pts.append(level_point([q[0],q[1]],q[2]))
		pts.append(level_point(rec.inside,rec.floor))
		if key=="renai":
			var crossing: Dictionary=buildings.renai_cross
			pts.append(level_point(rec.joint_inside,rec.floor))
			pts.append(level_point(rec.joint,rec.floor))
			pts.append(level_point(crossing.joint_inside,crossing.floor))
			pts.append(level_point(crossing.inside,crossing.floor))
		else:
			var back := level_point(rec.back,rec.floor)
			pts.append(back-Vector3(rec.inward[0],0,-float(rec.inward[1]))*.6)
			for j in range(data.courtyard_connections.school_back.size()-1,-1,-1):
				var step: Array=data.courtyard_connections.school_back[j]
				pts.append(level_point([step[0],step[1]],step[2]))
		await trial(key+"_from_delivery_court",pts)
	var school: Dictionary=buildings.jinma_classrooms
	var upper: Array=[level_point(school.inside,school.floor)]
	for step: Array in school.stairs_to_library:
		upper.append(level_point([step[0],step[1]],step[2]))
	await trial("reading_room_stair",upper)
	var fs:=FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE)
	fs.store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
