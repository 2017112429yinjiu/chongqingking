extends "../../scene_r24/day_one/verify.gd"

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory("res://verification_r24/road_shift/probe")
	if "--qa-still-frames" in OS.get_cmdline_user_args():RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(10)
	game=scene.gameplay
	lesson=game.lesson
	bike=game.scooter
	audit=lesson.audit
	var s:Vector3=lesson.SHOP_STOP
	lesson._place_vehicle(lesson.mentor,s,-PI/2)
	lesson._place_vehicle(bike,s+Vector3(-3.6,0,0),-PI/2)
	lesson.demo.walker.board()
	await frames(70)
	bike.enter(game.actor)
	bike.automation=true
	lesson.step=lesson.Step.TO_YARD
	lesson.demo.start_second_ride()
	await ride("two_riders_to_address")
	finish()
