extends "../../scene_r24/day_one/verify.gd"
const Unit=preload("res://scripts/unit_interior.gd")
func look_frame(label:String,point:Vector3)->void:
	game.actor.camera.look_at(point)
	game.actor._sync_angles()
	await frames(3)
	await capture(label)

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory("res://verification_r24/indoor_delivery")
	RenderingServer.render_loop_enabled=false
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	for i in 1000:
		if scene.gameplay:break
		await physics_frame
	game=scene.gameplay
	if not check("world",game!=null):end_run();return
	await frames(30)
	game.actor.begin_route_test(Unit.COURT+Vector3.UP*.16,Unit.LANDING)
	game.order=game.Order.CARRYING
	await frames(40)
	await look_frame("01_court_gate",Vector3(-54.9,18.05,19.5))
	tap(KEY_E)
	check("unit_gate_cannot_deliver",game.earnings==0 and not game.free_answered)
	if not await walk([Vector3(-54.90,16.44,19.5)],"cross_east_threshold"):end_run();return
	await look_frame("02_stair",Vector3(-60.8,20.85,19.5))
	if not await walk([Unit.LANDING],"climb_two_flights"):end_run();return
	check("real_2F_height",absf(game.actor.body.global_position.y-19.89)<.09,game.actor.body.global_position)
	await look_frame("03_201",Unit.DOOR_POINTS[0])
	await look_frame("03b_hallway",Vector3(-62.12,21.13,9.05))
	if not await walk([Vector3(-62.14,19.89,19.05),Vector3(-62.15,19.89,15.46)],"approach_202"):
		end_run();return
	await look_frame("04a_hall_door",Vector3(-63.01,21.21,13.7))
	if not await walk([Vector3(-62.15,19.89,13.70)],"cross_upper_hall"):end_run();return
	await look_frame("04_202",Unit.DOOR_POINTS[1])
	tap(KEY_E)
	check("different_flat_no_credit",game.earnings==0 and not game.free_answered)
	if not await walk([Vector3(-62.48,19.89,8.12)],"leave_via_back_gallery"):end_run();return
	await look_frame("05_gallery",Vector3(-66.88,19.45,8.02))
	if not await walk([Vector3(-65.34,19.89,8.04),Vector3(-70.65,17.25,8.04)],"descend_to_north_alley"):end_run();return
	await look_frame("06_back_door",Vector3(-62.12,21.20,9))
	if not await walk([Vector3(-65.34,19.89,8.04),Vector3(-62.48,19.89,8.12),Vector3(-62.15,19.89,19.42),Vector3(-63.86,19.89,19.62)],"back_alley_to_201"):end_run();return
	await look_frame("07_201_close",Unit.DOOR_POINTS[0])
	tap(KEY_E)
	check("resident_responds",game.free_answered and game.earnings==0)
	if not await walk([Vector3(-63.77,19.89,20.27)],"reach_201_shelf"):end_run();return
	await look_frame("07a_shelf",game.destination.global_position)
	tap(KEY_E)
	check("pay_after_release",game.earnings==0)
	await frames(86)
	await look_frame("07b_delivered",Unit.SHELVES[0]+Vector3.UP*.14)
	check("201_parcel_supported",game.bag.global_position.distance_to(Unit.SHELVES[0])<.005)
	check("201_paid_once",game.order==game.Order.DELIVERED and game.earnings==8)
	tap(KEY_E)
	check("repeated_input_no_extra_payment",game.earnings==8)
	game.select_free_address()
	game.order=game.Order.CARRYING
	if not await walk([Unit.LANDING,Vector3(-62.16,19.89,13.65),Vector3(-62.56,19.89,13.65)],"arrive_202"):end_run();return
	await look_frame("08_202_close",Unit.DOOR_POINTS[1])
	tap(KEY_E)
	if not await walk([Vector3(-62.55,19.89,14.55)],"reach_202_shelf"):end_run();return
	await look_frame("08a_shelf",game.destination.global_position)
	tap(KEY_E)
	await frames(86)
	check("202_parcel_supported",game.bag.global_position.distance_to(Unit.SHELVES[1])<.005)
	check("202_paid_at_its_own_door",game.order==game.Order.DELIVERED and game.earnings==16)
	if not await walk([Vector3(-62.16,19.89,19.5),Vector3(-54.9,16.44,19.5),Unit.COURT],"downstairs_back_to_bike"):end_run();return
	end_run()
func end_run()->void:
	FileAccess.open(output.path_join("route.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"\t"))
	quit(2 if ever_failed else 0)
