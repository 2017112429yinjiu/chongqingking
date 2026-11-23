extends "verify_shift.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene=scene
	for tick in 1200:
		if scene.gameplay:break
		await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	audit=lesson.audit
	bike=game.scooter
	await frames(28)
	check("practice_only_no_personal_checkpoint",lesson.record_path=="" and lesson.step==lesson.Step.LAST_METRES)
	if not await attend("PUPIL_UNLOAD",false):finish();return
	if not await walk([bike.global_position+Vector3(0,0,.86)],"walk_to_parked_box"):finish();return
	tap(KEY_E)
	await frames(124)
	if not check("collected_own_order",lesson.demo.student_retrieved):finish();return
	if not await attend("PUPIL_DELIVERS",true):finish();return
	check("guide_at_201",lesson.demo.parcel.global_position.distance_to(lesson.demo.hooks[0])<.6 and lesson.demo.walker.global_position.y>19.7)
	if not await walk([lesson.demo.door.point+Vector3(.35,-1.35,-.10)],"walk_to_flat"):finish();return
	game.actor.camera.look_at(lesson.demo.door.point)
	game.actor._sync_angles()
	tap(KEY_E)
	await frames(137)
	check("practice_knocked",lesson.demo.student_knocked)
	if not await walk([lesson.demo.hooks[1]+Vector3(.05,-1.1,.40)],"pupil_hook"):finish();return
	game.actor.camera.look_at(lesson.demo.hooks[1])
	game.actor._sync_angles()
	tap(KEY_E)
	await frames(140)
	check("practice_paid_at_flat",lesson.step==lesson.Step.RETURN and game.earnings==8)
	finish()
