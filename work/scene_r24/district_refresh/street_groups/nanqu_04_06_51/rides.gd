extends "../houci_14_16/ride_connectors.gd"

const NANQU_SITE := "res://assets/district_500/nanqu-04-06-51.json"
const DECK := "COL_R24_LinkDeck_R24_link_asphalt"
const APPROACH := "COL_Nanqu_RaisedWestApproach"

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	game=scene.gameplay
	bike=game.scooter
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(NANQU_SITE))
	var points: Array=plan.bike_path
	var results := {}
	bike.enter(game.actor)
	bike.automation=true
	var pieces := ["approach_to_51","under_rail_04"]
	if "--qa-nanqu-both-wheel-lines" in OS.get_cmdline_user_args():
		pieces.append("under_rail_04_outer_wheel_line")
	for piece: String in pieces:
		var route := points.slice(0,10) if piece=="approach_to_51" else points.slice(12)
		var allowed := [DECK,APPROACH] if piece=="approach_to_51" else [DECK]
		if piece=="under_rail_04_outer_wheel_line" or (piece=="under_rail_04" and "--qa-nanqu-outer-wheel-line" in OS.get_cmdline_user_args()):
			route = lane_offset(route)
		var forward := await monitored_drive(route,allowed)
		route.reverse()
		var reverse := await monitored_drive(route,allowed)
		results[piece]={"forward":forward,"closed_reverse_test":reverse}
		for direction: String in ["forward","closed_reverse_test"]:
			var outcome: Dictionary=results[piece][direction]
			check(piece+"_"+direction,outcome.pass,
				{"reached":outcome.reached,"targets":outcome.targets,"airborne_frames":outcome.airborne_frames,
				"distance_m":outcome.distance_m,"last_contact":outcome.last_contact})
	var supports := []
	for expected: Array in plan.planter_contacts:
		var hit := support(world(expected),.019,.12)
		supports.append({"expected_enu":expected,"found":hit})
	check("flower_box_corners_on_footway",supports.all(func(entry: Dictionary) -> bool:
		return entry.found.get("body","")=="COL_Nanqu_RiverFootway"),supports)
	FileAccess.open(output.path_join("rides.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"identity":scene.scene_identity.district_500,
		"results":results,"support_corners":supports,"checks":checks},"  "))
	quit(2 if ever_failed else 0)

func monitored_drive(route: Array, allowed: Array) -> Dictionary:
	var walls := {}
	var capture := func() -> void:
		for idx in bike.get_slide_collision_count():
			var hit: KinematicCollision3D = bike.get_slide_collision(idx)
			var n: Vector3=hit.get_normal()
			var body: String=String(hit.get_collider().get_parent().name)
			if n.y>.67 and body in allowed:
				continue
			if not walls.has(body):
				walls[body]={"samples":0,"first":str(hit.get_position()),"normal":str(n)}
			walls[body].samples+=1
	var callback:=capture
	physics_frame.connect(callback)
	var result := await drive(route,allowed)
	physics_frame.disconnect(callback)
	result["wall_hits"]=walls
	var sweep := KinematicCollision3D.new()
	var ahead: Vector3 = -bike.global_basis.z
	if not result.pass and bike.test_move(bike.global_transform,ahead*.38,sweep,.001,false,8):
		var hits := []
		for i in sweep.get_collision_count():
			hits.append({"mesh":str(sweep.get_collider(i).get_parent().name),
				"normal":str(sweep.get_normal(i)),"position":str(sweep.get_position(i))})
		result["stationary_sweep"]=hits
	return result

func lane_offset(rows: Array) -> Array:
	var variant := rows.duplicate(true)
	for i in range(1,rows.size()-1):
		var xy := world(rows[i])
		var touch := world(rows[i+1])-world(rows[i-1])
		touch.y=0.
		var curb := touch.normalized().cross(Vector3.UP)
		var distance := .48 * smoothstep(-155.,-149.,xy.x) * (1.-smoothstep(-135.,-130.,xy.x))
		xy += curb*distance
		var hit := support(xy)
		variant[i]=[xy.x,-xy.z,hit.get("y",xy.y)]
	return variant
