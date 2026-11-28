extends "../../continuous_site_walk.gd"

const LOW := [[-171.62,-111.25],[-171.62,-108.85],[-171.62,-106.45],
	[-171.62,-104.05],[-171.62,-101.65],[-171.62,-99.25],[-171.62,-96.85]]
const UPPER := "COL_Nanqu_RiverFootway"
const LOW_ROAD_CONTEXT := [[-187.29,-126.49],[-185.20,-123.60],[-181.50,-120.85]]

func follow(label: String, route: Array[Vector3]) -> Dictionary:
	var actor = scene.explorer
	actor.set_walk_origin(route[0]+Vector3.UP*.035,route[1]+Vector3.UP)
	await frames(20)
	var origin: Vector3 = actor.body.global_position
	var going := await leg_without_placement(label+"_out",route.slice(1))
	var turn: Vector3 = actor.body.global_position
	var returning := {}
	if going.pass:
		route.reverse()
		returning = await leg_without_placement(label+"_back",route.slice(1))
		check(label+"_return_same_origin",actor.body.global_position.distance_to(origin)<.47,enu(actor.body.global_position))
	actor.end_route_test()
	return {"start_enu":enu(origin),"turn_enu":enu(turn),"out":going,"back":returning,"teleports_between_legs":0}

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var low: Array[Vector3] = []
	var low_columns := []
	var context_columns := []
	for en: Array in LOW_ROAD_CONTEXT:
		context_columns.append({"east_north":en,"layers":column(en)})
	for en: Array in LOW:
		low.append(ground_point(en,0.))
		low_columns.append({"enu":enu(low.back()),"layers":column(en)})
	var road: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/nanqu-04-06-51.json"))
	var upper: Array[Vector3] = []
	var upper_columns := []
	for row: Array in road.public_walk.slice(8,14):
		var hits := column(row.slice(0,2))
		var existing := hits.filter(func(hit: Array) -> bool: return hit[0] == UPPER and hit[2] > .8)
		upper_columns.append({"registered_before_regrade_enu":row,"layers":hits,
			"active_walkway_support":existing[0][1] if existing.size() == 1 else null})
		if existing.size() == 1:
			upper.append(Vector3(row[0],existing[0][1],-row[1]))
	check("six_expected_upper_deck_ground_contacts",upper.size()==6,upper.size())
	var lower_result := await follow("52_existing_low_exterior",low)
	var upper_result := {}
	if upper.size()==6:
		upper_result = await follow("52_neighboring_upper_public_walkway",upper)
		var sampled := {}
		for walk: Dictionary in walks:
			if not String(walk.id).begins_with("52_neighboring_upper"):
				continue
			var contacts := 0
			for row: Array in walk.trace_enu:
				var position := Vector3(row[0],row[2],-row[1])
				var probe := PhysicsRayQueryParameters3D.create(position+Vector3.UP*.16,position-Vector3.UP*.27,1)
				var hit := scene.get_world_3d().direct_space_state.intersect_ray(probe)
				if not hit.is_empty() and hit.collider.get_parent().name==UPPER: contacts+=1
			sampled[walk.id] = [contacts,walk.trace_enu.size()]
			check(walk.id+"_support",contacts==walk.trace_enu.size(),sampled[walk.id])
		upper_result["route_contacts"] = sampled
	FileAccess.open(output.path_join("52-layers.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"low_outside_footprint":lower_result,"adjacent_upper_walkway":upper_result,
		"lower_columns":low_columns,"registered_low_road_context":context_columns,
		"upper_columns":upper_columns,"checks":checks,"traces":walks,
		"scope":"Different game EN paths. Relative tier evidence comes from independent field views, not comparing their absolute game heights."},"  "))
	quit(2 if ever_failed else 0)
