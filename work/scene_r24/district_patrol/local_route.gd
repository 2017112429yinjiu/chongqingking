extends "../../scene_r24/vertical_run/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	route=game.passage
	await frames(30)
	if not check("isolated",lesson.record_path.is_empty() and route.stage==route.Stage.COLLECT):end_run();return
	if not await walk([Vector3(-54.9,16.44,19.5),Unit.LANDING,Vector3(-62.15,19.89,19.05),Vector3(-62.15,19.89,14.60),Vector3(-62.54,19.89,14.56)],"collect_in_202"):end_run();return
	await face(route.pickup.global_position)
	tap(KEY_E)
	check("collected",route.stage==route.Stage.CARRY)
	if not await walk([Vector3(-62.07,19.89,17.52)],"find_home_stair"):end_run();return
	await shot("01_new_entrance",Vector3(-60.44,21.15,17.52))
	if not await walk([Vector3(-55.55,22.90,17.52)],"resident_climb"):end_run();return
	await shot("02_look_back",Vector3(-60.62,20.65,17.52))
	if not await walk([Vector3(-55.56,22.90,16.08),Vector3(-60.09,22.90,16.08),Vector3(-60.09,22.90,14.38),Vector3(-59.30,22.90,14.14)],"resident_to_301"):end_run();return
	await shot("03_recipient",route.DOOR)
	tap(KEY_E)
	check("door_answered",game.free_answered)
	if not await walk([Vector3(-59.26,22.90,14.94)],"reach_shelf"):end_run();return
	await face(game.destination.global_position)
	tap(KEY_E)
	await frames(110)
	check("home_delivery_settled",game.earnings==40 and route.stage==route.Stage.IDLE)
	if not await walk([Vector3(-60.1,22.90,14.55),Vector3(-60.1,22.90,16.08),Vector3(-55.55,22.90,16.08),Vector3(-55.55,22.90,17.52),Vector3(-62.10,19.89,17.52),Vector3(-62.10,19.89,14.6)],"home_stair_down"):end_run();return
	end_run()
