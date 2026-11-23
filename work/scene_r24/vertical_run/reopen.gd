extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	var source:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--from="):source=arg.trim_prefix("--from=")
	var checkpoint:=output.path_join("local.cfg")
	if not check("independent_save",DirAccess.copy_absolute(source,checkpoint)==OK):finish_run();return
	lesson=preload("res://scripts/day_one.gd").new()
	game.add_child(lesson)
	game.lesson=lesson
	lesson.setup(game,checkpoint)
	await frames(24)
	var route:Node3D=game.passage
	if "--counter" in OS.get_cmdline_user_args():
		if not await walk([Vector3(-25.3,16,21.6),Vector3(-25.8,15.5,29),Vector3(-25.9,14.7,35),Vector3(-24.6,14,40.5),Vector3(-25.3,12.7,48),Vector3(-24.7,12.3,52),Vector3(-25.3,12,55.25),Vector3(-25.1,12,57.1),scene._pickup+Vector3(.7,0,-.2)],"graduation_to_counter"):finish_run();return
		tap(KEY_G)
		check("lunch_still_available",game.lunch.preview)
		tap(KEY_B)
		check("choose_passage_instead",route.offered and not game.lunch.preview and game.earnings==24)
		tap(KEY_B)
		check("cancel_offer",not route.offered and route.stage==route.Stage.IDLE)
		tap(KEY_B)
		tap(KEY_E)
		check("normal_counter_accepts",route.stage==route.Stage.COLLECT and game.bag.visible and game.bag.global_position.distance_to(preload("res://scripts/unit_interior.gd").SHELVES[1])<.01)
		var cfg:=ConfigFile.new()
		cfg.load(checkpoint)
		check("clean_checkpoint",cfg.get_value("passage","stage")==route.Stage.COLLECT and not game.shop.available())
	else:
		if not check("on_bridge_with_cook_order",route.stage==route.Stage.CARRY and game.actor.body.global_position.distance_to(Vector3(-72.1,23.92,14.36))<.55 and game.bag.visible and game.earnings==24):finish_run();return
		if not await walk([Vector3(-65.6,23.92,14.35),Vector3(-62.93,22.9,14.35),Vector3(-59.30,22.9,14.14)],"resume_down_to_301"):finish_run();return
		game.actor.camera.look_at(route.DOOR)
		game.actor._sync_angles()
		tap(KEY_E)
		if not await walk([Vector3(-59.26,22.90,14.94)],"resume_to_shelf"):finish_run();return
		game.actor.camera.look_at(game.destination.global_position)
		game.actor._sync_angles()
		tap(KEY_E)
		await frames(95)
		tap(KEY_E)
		var cfg:=ConfigFile.new()
		cfg.load(checkpoint)
		check("settled_once_after_reopen",route.stage==route.Stage.IDLE and game.earnings==40 and cfg.get_value("shift","deliveries")==4 and cfg.get_value("passage","stage")==route.Stage.IDLE)
	finish_run()
func finish_run()->void:
	FileAccess.open(output.path_join("reopen.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"\t"))
	quit(2 if ever_failed else 0)
