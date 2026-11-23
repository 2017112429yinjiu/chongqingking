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
	var former:bool="--former" in OS.get_cmdline_user_args()
	var downhill:bool="--down-court" in OS.get_cmdline_user_args()
	var court:bool="--cross-court" in OS.get_cmdline_user_args() or downhill
	var s:=Vector3(9,11.9,58) if former else (Vector3(-41,16,23.3) if court else Vector3(11.0,11.25,62.75))
	var yaw:=PI/2 if former else (0. if court else 1.04)
	if downhill:
		s=Vector3(-44.5,16.4,18.72)
		yaw=-PI/2
	var rear:=Basis(Vector3.UP,yaw)*Vector3.BACK
	lesson._place_vehicle(lesson.mentor,s,yaw)
	lesson._place_vehicle(bike,s+rear*3.6,yaw)
	lesson.demo.walker.board()
	await frames(70)
	bike.enter(game.actor)
	bike.automation=true
	lesson.step=lesson.Step.TO_YARD
	lesson.demo.start_second_ride()
	var route:=PackedVector3Array()
	if former:route=PackedVector3Array([Vector3(-5,11.8,58),Vector3(-22.6,11.6,57.8)])
	elif downhill:route=PackedVector3Array([Vector3(-42,16.5,19.4),Vector3(-40.4,16.2,21.8),Vector3(-40.2,15.65,25.1),Vector3(-43.3,15.45,26.1)])
	elif court:route=PackedVector3Array([Vector3(-41,16.4,19.8),Vector3(-42.7,16.5,18.6),Vector3(-46.7,16.4,19)])
	else:
		var layout=JSON.parse_string(FileAccess.get_file_as_string("res://assets/connections_r24/layout.json"))
		for row in layout.stairs:
			if "Central" in row.lane and int(row.row)>2:
				route.append(Vector3(row.point[0],row.point[1],row.point[2]))
		route.append_array(PackedVector3Array([Vector3(-20,14.9,34),Vector3(-20,15.6,29.7)]))
	lesson.mentor.guide_to(route)
	await ride("real_street_crossing")
	finish()
