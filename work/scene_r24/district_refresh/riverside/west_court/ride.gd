extends "../../../district_500/routes.gd"

func route_plan() -> Dictionary:
	var site: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/west-court.json"))
	var path: Array = site.walk_plan.ramp.duplicate()
	path.push_front([-135.8, -200.87])
	return {"west_court_east_ramp": path}
