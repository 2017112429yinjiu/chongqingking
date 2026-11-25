extends "../../scene_r24/street_blocks/views.gd"

func reopen(file: String) -> void:
	if is_instance_valid(scene):
		scene.queue_free()
		await process_frame
	scene=load("res://main.tscn").instantiate()
	scene.district_500_enabled=true
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	game=scene.gameplay
	lesson=preload("res://scripts/day_one.gd").new()
	game.add_child(lesson)
	game.lesson=lesson
	lesson.setup(game,file)
	await frames(26)

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	var file:=output.path_join("shift.cfg")
	var cfg:=ConfigFile.new()
	cfg.set_value("shift","step",6)
	cfg.set_value("shift","round",2)
	cfg.set_value("shift","deliveries",3)
	cfg.set_value("shift","earnings",24)
	cfg.save(file)
	await reopen(file)
	var job=game.shancheng
	check("previous_save_offers_job",job.available())
	var src: Array=job.stops[0].approach
	var dst: Array=job.stops[1].approach
	scene.explorer.begin_route_test(Vector3(src[0],src[2],-src[1]),job.sender.global_position)
	await frames(28)
	check("interact_to_save_pickup",game.manager.interact() and job.stage==job.Stage.CARRYING)
	DirAccess.copy_absolute(file,output.path_join("picked_up.cfg"))
	await reopen(file)
	job=game.shancheng
	check("resumed_on_lane_with_bag",job.stage==job.Stage.CARRYING and game.earnings==24 and scene.explorer.body.global_position.distance_to(Vector3(src[0],src[2],-src[1]))<.8)
	scene.explorer.begin_route_test(Vector3(dst[0],dst[2],-dst[1]),job.receiver.global_position)
	await frames(28)
	check("deliver_after_reopening",game.manager.interact() and game.earnings==30 and game.delivered_count==4)
	await reopen(file)
	job=game.shancheng
	check("restored_receipt_and_one_payment",job.stage==job.Stage.DELIVERED and job.delivered_parcel.visible and game.earnings==30 and game.delivered_count==4)
	FileAccess.open(output.path_join("checkpoint.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
