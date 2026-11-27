extends "../../../continuous_site_walk.gd"

func site_plan() -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://assets/district_500/collectibles-market.json"))
	var side := "--qa-market-side" in OS.get_cmdline_user_args()
	return {"id":"zhongxing_collectibles_side" if side else "zhongxing_collectibles",
		"stations":plan.side_route_east_north if side else plan.route_east_north,
		"street_focus":plan.street_eye_target_east_north_up,
		"return_focus":plan.return_eye_target_east_north_up,
		"destination_y":plan.side_landing_floor_m if side else plan.hall_floor_m}
