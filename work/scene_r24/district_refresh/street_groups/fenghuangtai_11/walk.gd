extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/fenghuangtai-11.json"

func site_plan() -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var points: Array = plan.site_walk
	var arrival: Array = points.back()
	var start: Array = points.front()
	return {"id":"fenghuangtai_public_turn", "stations":points, "destination_y":arrival[2],
		"street_focus":[arrival[0],arrival[1],arrival[2]+.7], "return_focus":[start[0],start[1],start[2]+1.64]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var report := await super.leg_without_placement(label, goals)
	var trace: Array = walks.back().trace_enu
	var missed := []
	for row: Array in trace:
		var origin := Vector3(row[0],row[2]+.22,-row[1])
		var query := PhysicsRayQueryParameters3D.create(origin,origin-Vector3.UP*.75,1)
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
		var body := "" if hit.is_empty() else String(hit.collider.get_parent().name)
		if body!="COL_Fenghuangtai11_StoneTurn":
			missed.append({"position":row,"body":body})
	check(label+"_stone_support",missed.is_empty(),{"samples":trace.size(),"missed":missed})
	return report
