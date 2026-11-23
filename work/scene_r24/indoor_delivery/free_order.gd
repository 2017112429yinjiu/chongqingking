extends "../../scene_r24/day_one/verify.gd"
const Unit=preload("res://scripts/unit_interior.gd")
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	var source:String=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--checkpoints="):source=arg.trim_prefix("--checkpoints=")
	var path:=output.path_join("fourth_order.cfg")
	if DirAccess.copy_absolute(source.path_join("completed.cfg"),path)!=OK:quit(3);return
	lesson=preload("res://scripts/day_one.gd").new()
	game.add_child(lesson)
	game.lesson=lesson
	lesson.setup(game,path)
	await frames(35)
	var lane:=[Vector3(-25.3,16,21.6),Vector3(-25.8,15.5,29),Vector3(-25.9,14.7,35),Vector3(-24.6,14,40.5),Vector3(-25.3,12.7,48),Vector3(-24.7,12.3,52),Vector3(-25.3,12,55.25),Vector3(-25.1,12,57.1)]
	if not await walk(lane+[scene._pickup+Vector3(.7,0,-.2)],"last_tutorial_bay_to_shop"):done();return
	tap(KEY_E)
	check("first_free_order_has_address_and_real_ticket",game.order==game.Order.PREPARING and "201" in game.bag.ticket.text and "008" in game.bag.ticket.text,game.bag.ticket.text)
	await frames(280)
	tap(KEY_E)
	await frames(85)
	tap(KEY_E)
	await frames(6)
	if not check("packed_free_order_in_hand",game.order==game.Order.CARRYING and game.bag.visible and game.earnings==24):done();return
	lane.reverse()
	if not await walk(lane+[Vector3(-48.5,16.4,19.65),Unit.COURT,Vector3(-54.9,16.44,19.50),Unit.LANDING,Vector3(-63.87,19.89,19.65)],"carry_order_from_noodle_shop_up_to_201"):done();return
	game.actor.camera.look_at(game.destination.global_position)
	game.actor._sync_angles()
	tap(KEY_E)
	check("201_customer_confirms_order",game.free_answered and game.earnings==24)
	if not await walk([Vector3(-63.77,19.89,20.27)],"reach_household_shelf"):done();return
	game.actor.camera.look_at(game.destination.global_position)
	game.actor._sync_angles()
	tap(KEY_E)
	await frames(38)
	await capture("pupil_sets_meal_down")
	tap(KEY_E)
	check("release_still_pending",game.earnings==24 and game.shelf_time>=0)
	await frames(56)
	var cfg:=ConfigFile.new()
	cfg.load(path)
	check("supported_and_paid_once",game.earnings==32 and game.delivered_count==4 and cfg.get_value("shift","deliveries")==4 and game.bag.global_position.distance_to(Unit.SHELVES[0])<.006)
	await capture("fourth_order_delivered")
	done()
func done()->void:
	FileAccess.open(output.path_join("free_order.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"\t"))
	quit(2 if ever_failed else 0)
