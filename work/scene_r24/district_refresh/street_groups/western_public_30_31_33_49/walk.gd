extends "../liangtingzi_45_46/walk.gd"

func verification_site() -> Dictionary:
	return {"resource":"res://assets/district_500/western-public-30-31-33-49.json","surfaces":{
		"30":"COL_Western30_OutdoorStoneFlags","31":"COL_Western31_OutdoorStoneFlags",
		"33":"COL_Western33_OutdoorStoneFlags","49":"COL_Western49_OutdoorStoneFlags",
		"30-garden":"COL_Western30-garden_OutdoorStoneFlags","31-garden":"COL_Western31-garden_OutdoorStoneFlags"}}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	if label=="33_public_out" and result.pass:
		var field_path: String = get_script().resource_path.get_base_dir().path_join("field.json")
		var field: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(field_path))
		var target: Array = field.registered_2015_wall_pipe.en
		var actor_at: Vector3 = scene.explorer.body.global_position
		var distance := Vector2(actor_at.x,-actor_at.z).distance_to(Vector2(target[0],target[1]))
		check("walked_to_2015_pipe",distance>.43 and distance<1.45,distance)
		check("2015_pipe_loaded",scene.find_child("Western33_LocatedPipeAndClamps",true,false)!=null,target)
	if label=="33_public_return" and result.pass:
		var field_path: String = get_script().resource_path.get_base_dir().path_join("field.json")
		var field: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(field_path))
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(verification_site().resource))
		var connector: Array[Vector3] = []
		for station: Array in field.public_connector_en:
			connector.append(ground_point(station,.12))
		var origin: Array = plan.walks["33"][0]
		connector[0] = Vector3(origin[0],origin[2],-origin[1])
		for plot: String in ["30","31"]:
			var entry: Array = plan.walks[plot][0]
			var target := Vector3(entry[0],entry[2],-entry[1])
			var out := connector.slice(1)
			out.append(target)
			var joined := await super.leg_without_placement("33_to_"+plot+"_public_junction",out)
			if joined.pass:
				var back := connector.duplicate()
				back.reverse()
				await super.leg_without_placement(plot+"_junction_back_to_33",back)
	return result
