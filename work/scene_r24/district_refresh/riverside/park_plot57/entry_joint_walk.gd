extends "../../continuous_site_walk.gd"

const PLAN := "res://assets/district_500/park-plot57.json"
const STREET := "res://assets/district_500/west-ramp.json"
const OLD_WALL := "COL_WestPlayground_PerimeterSupport"
const RETURN := "COL_Park57_StreetEntryReturn"

func site_plan() -> Dictionary:
	var control: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var street: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(STREET)).playground.street_access
	var before := "--qa-without-park-plot57" in OS.get_cmdline_user_args()
	var access: Array = street.route_east_north
	var route := access.slice(0, 4)
	var joint: Array = control.street_entry_return.section_east_north_lower_upper
	route.append_array([[-154.10, -167.40], [-153.71, -167.70], [-153.71, -168.56], access[4]])

	var space := scene.get_world_3d().direct_space_state
	var across := Vector2(-.1145, -.9934)
	for section: Array in joint.slice(1, 4):
		var center := Vector2(section[0], section[1])
		var ramp := center - across * .065
		var sand := center + across * .065
		var ramp_floor: Array = column([ramp.x, ramp.y])
		var sand_floor: Array = column([sand.x, sand.y])
		if not check("ground_either_side", not ramp_floor.is_empty() and not sand_floor.is_empty(),
			[ramp_floor, sand_floor]):
			continue
		var riser := float(ramp_floor[0][1]) - float(sand_floor[0][1])
		var rays := []
		for elevation: float in [section[2] - .06, (section[2] + section[3]) * .5, section[2] + .24, section[2] + .90]:
			var from := Vector3(ramp.x, elevation, -ramp.y)
			var to := Vector3(sand.x, elevation, -sand.y)
			var query := PhysicsRayQueryParameters3D.create(from, to, 1)
			var hit := space.intersect_ray(query)
			rays.append([elevation, String(hit.collider.get_parent().name) if not hit.is_empty() else ""])
		var contact := {"ramp_en": [ramp.x, ramp.y], "sand_en": [sand.x, sand.y],
			"floor": [ramp_floor[0], sand_floor[0]], "riser_m": riser, "rays": rays}
		check("paving_on_both_sides", riser > .01 and riser < .06, contact)
		check("old_wall_blocks_body" if before else "stone_riser_and_open_body_clearance",
			(rays[2][1] == OLD_WALL and rays[3][1] == OLD_WALL) if before
				else (rays[1][1] == RETURN and rays[2][1] == "" and rays[3][1] == ""), contact)

	return {"id": "across_west_park_street_entry_joint", "stations": route,
		"street_focus": street.street_focus_east_north_up, "destination_y": -5.83}
