extends "../../continuous_site_walk.gd"

var playground: Dictionary
var street_axis_begin: Vector2
var street_axis_direction: Vector2

func site_plan() -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://assets/district_500/west-ramp.json"))
	playground = plan.playground
	if "--west-street-court" in OS.get_cmdline_user_args():
		var street_access: Dictionary = playground.street_access
		street_axis_begin = Vector2(street_access.registered_segment_east_north[0][0],
			street_access.registered_segment_east_north[0][1])
		var b: Vector2 = Vector2(street_access.registered_segment_east_north[1][0],
			street_access.registered_segment_east_north[1][1])
		street_axis_direction = (b-street_axis_begin).normalized()
		var clearances := []
		for en: Array in street_access.route_east_north:
			clearances.append(street_offset(en))
		check("starts_on_park_side_shoulder", absf(clearances[0]-street_access.shoulder_centre_offset_m)<.02,
			{"osm_way":street_access.osm_way,"axis_distances_m":clearances,
			"curb_offset_m":street_access.south_curb_offset_m,"opening":street_access.entry_opening_east_north})
		check("route_stays_off_carriageway",clearances.all(func(d: float) -> bool:
			return d > street_access.south_curb_offset_m+.75),clearances)
		return {"id":"west_binjiang_street_gate","stations":street_access.route_east_north,
			"street_focus":street_access.street_focus_east_north_up,"destination_y":playground.sand_destination_y}
	var stations: Array = plan.street_route_east_north
	var destination: float = plan.deck_elevation_m
	if "--west-sand-continuous" in OS.get_cmdline_user_args():
		stations.append_array(playground.sand_path_east_north)
		destination = playground.sand_destination_y
	return {"id":"west_park_ramp","stations":stations,
		"street_focus":plan.street_focus_east_north_up,"destination_y":destination}

func street_offset(en: Array) -> float:
	return (Vector2(en[0],en[1])-street_axis_begin).cross(street_axis_direction)

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label, goals)
	if label.begins_with("west_binjiang_street_gate"):
		var minimum := INF
		for sample: Array in walks[-1].trace_enu:
			minimum = minf(minimum,street_offset(sample))
		check(label+"_sampled_trace_stays_off_road",
			minimum > playground.street_access.south_curb_offset_m+.50,{"min_axis_distance_m":minimum})
	return result

func eye_frame(label: String, focus: Variant) -> void:
	if label == "street" and "--west-sand-pair-only" in OS.get_cmdline_user_args():
		await fixed_view("registered_sand",point(playground.sand_eye_east_north_up),
			point(playground.sand_target_east_north_up))
		return
	var street_access := "--west-street-court" in OS.get_cmdline_user_args()
	if street_access and label in ["street","street_return"]:
		var gate: Array = playground.street_access.route_east_north[1]
		scene.explorer.aim_route_test(Vector3(gate[0]+.80,0.,-gate[1]+.65))
		focus = null
	await super.eye_frame(label, focus)
	if label == "street" and (not street_access or "--west-street-views" in OS.get_cmdline_user_args()):
		if not street_access:
			await fixed_view("registered_ramp_margin",Vector3(-148.6,-4.20,181.0),
				ground_point([-136.0,-200.9],1.2))
		await fixed_view("registered_blue",point(playground.blue_eye_east_north_up),
			point(playground.blue_target_east_north_up))
		await fixed_view("registered_sand",point(playground.sand_eye_east_north_up),
			point(playground.sand_target_east_north_up))
	if label == "inside_look_back":
		var sand := street_access or "--west-sand-continuous" in OS.get_cmdline_user_args()
		var target := point(playground.sand_target_east_north_up if sand else playground.blue_target_east_north_up)
		scene.explorer.aim_route_test(target)
		await super.eye_frame("player_sand_turn" if sand else "player_blue_turn",null)

func fixed_view(label: String, eye: Vector3, target: Vector3) -> void:
	await shot(label,eye,target)
	scene.explorer.camera.make_current()
	view_positions.append({"frame":label+".png","eye_enu":enu(eye),
		"target_enu":enu(target),"pixel_size":str(root.size)})

func point(position: Array) -> Vector3:
	return Vector3(position[0],position[2],-position[1])
