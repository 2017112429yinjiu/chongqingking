extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/changbin-55.json"

var plan: Dictionary
var axis_origin: Vector2
var axis: Vector2

func site_plan() -> Dictionary:
	plan=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var rows: Array=plan.walk.duplicate(true)
	var park := "--changbin-55-park" in OS.get_cmdline_user_args()
	var destination_y: float=rows[-1][2]
	if park:
		var park_plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/west-ramp.json"))
		rows.reverse()
		rows.pop_back()
		rows.append_array(park_plan.playground.street_access.route_east_north.slice(2))
		destination_y=park_plan.playground.sand_destination_y
	var a: Array=plan.road_line_en[0]
	var b: Array=plan.road_line_en[1]
	axis_origin=Vector2(a[0],a[1])
	axis=(Vector2(b[0],b[1])-axis_origin).normalized()
	var last: Array=rows.back()
	var first: Array=rows[0]
	return {"id":"changbin55_park" if park else "changbin55_shoulder",
		"stations":rows,"destination_y":destination_y,
		"street_focus":[last[0],last[1],destination_y+1.55],
		"return_focus":[first[0],first[1],first[2]+1.35]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var samples: Array=walks.back().trace_enu
	var clearance := INF
	var support := {}
	for row: Array in samples:
		clearance=minf(clearance,(Vector2(row[0],row[1])-axis_origin).cross(axis))
		var point := Vector3(row[0],row[2]+.18,-row[1])
		var ray := PhysicsRayQueryParameters3D.create(point,point-Vector3.UP*.90,1)
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
		var mesh := "unhit" if hit.is_empty() else String(hit.collider.get_parent().name)
		support[mesh]=int(support.get(mesh,0))+1
	check(label+"_stays_off_carriageway",clearance>=5.9 and support.get("unhit",0)==0,{"samples":samples.size(),"road_axis_en_distance_min_m":clearance,"support":support})
	return result
