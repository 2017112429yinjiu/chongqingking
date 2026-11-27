extends "../../continuous_site_walk.gd"

const LOWER_OUTSIDE := [[-171.62,-111.25],[-171.62,-108.85],[-171.62,-106.45],
	[-171.62,-104.05],[-171.62,-101.65],[-171.62,-99.25],[-171.62,-96.85]]

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name() != "headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var samples := []
	for row in range(-4,5):
		for col in range(-4,5):
			var point := [-181.220437+col*2.4,-101.650443+row*2.4]
			samples.append({"east_north":point,"support":column(point)})
	check("outside_ground_section_81",samples.size()==81,samples.size())
	var route: Array[Vector3] = []
	for station: Array in LOWER_OUTSIDE:
		var ground := ground_point(station,0.)
		route.append(ground)
	var actor = scene.explorer
	actor.set_walk_origin(route[0]+Vector3.UP*.035,route[1]+Vector3.UP)
	await frames(16)
	var start: Vector3 = actor.body.global_position
	var outward := await leg_without_placement("52_exterior_terrain_out",route.slice(1))
	var back := {}
	var turn := Vector3.ZERO
	if outward.pass:
		turn = actor.body.global_position
		if graphics:
			actor.aim_route_test(route[2])
			await eye_frame("52-actual-look-back",null)
		route.reverse()
		back = await leg_without_placement("52_exterior_terrain_return",route.slice(1))
		check("52_return_same_origin",actor.body.global_position.distance_to(start)<.47,enu(actor.body.global_position))
	actor.end_route_test()
	FileAccess.open(output.path_join("plot52-sections-and-walk.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"scope":"Game terrain east of the opaque hillside area; actual building or portal dimensions undetermined.",
		"sections":samples,"out":outward,"back":back,"start_enu":enu(start),"turn_enu":enu(turn),
		"checks":checks,"traces":walks,"teleports_between_legs":0},"  "))
	quit(2 if ever_failed else 0)
