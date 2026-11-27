extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/nanqu-04-06-51.json"

func site_plan() -> Dictionary:
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var rows: Array=plan.public_walk
	var point: Array=rows.back()
	var next: Array=rows[2]
	return {"id":"nanqu_river_edge","stations":rows,"destination_y":point[2],
		"street_focus":[next[0],next[1],next[2]+1.4],"return_focus":[rows[-3][0],rows[-3][1],rows[-3][2]+1.4]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var samples: Array=walks.back().trace_enu
	var contacts := {}
	for row: Array in samples:
		var point := Vector3(row[0],row[2]+.20,-row[1])
		var query := PhysicsRayQueryParameters3D.create(point,point-Vector3.UP*.65,1)
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
		var body := "unhit" if hit.is_empty() else String(hit.collider.get_parent().name)
		contacts[body]=int(contacts.get(body,0))+1
	var walk_name := "COL_Nanqu_RiverFootway"
	check(label+"_continuous_footway",int(contacts.get(walk_name,0))==samples.size(),
		{"samples":samples.size(),"by_contact":contacts})
	return result
