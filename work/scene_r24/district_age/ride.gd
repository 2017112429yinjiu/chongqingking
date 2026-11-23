extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay
	lesson=game.lesson
	bike=game.scooter
	audit=lesson.audit
	var line:Array=[]
	var which:="school"
	if "--southeast" in OS.get_cmdline_user_args():which="southeast"
	if "--fork" in OS.get_cmdline_user_args():which="fork"
	if "--west-original" in OS.get_cmdline_user_args():which="west_cut"
	if "--west-entry" in OS.get_cmdline_user_args():which="west_entry"
	for site in ["east_old","east_bypass","corner_old","corner_bypass"]:
		if ("--"+site) in OS.get_cmdline_user_args():which=site
	if which=="east_old":line=[[49.6,21.],[49.,19.],[47.2,15.9],[45.6,13.2],[43.8,10.1],[40.2,3.9],[38.4,.8]]
	elif which=="east_bypass":
		line=[[49.6,21.]]
		for q:Array in JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_age/east_passage.json")):line.append([q[0],-q[1]])
		if "--reverse" in OS.get_cmdline_user_args():line.reverse()
	elif which=="corner_old":line=[[79.6,-21.1],[82.,-18.3],[85.4,-14.2],[87.0,-12.25],[89.1,-9.77],[91.,-7.5]]
	elif which=="corner_bypass":
		var curve:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_age/blue_block_bend.json"))
		line=[[76.8,-24.72]]
		var previous:=Vector2(76.8,24.72)
		for q:Array in curve:
			var pt:=Vector2(q[0],q[1])
			if pt.distance_to(previous)>2.35:
				line.append([q[0],-q[1]])
				previous=pt
		line.append([97.62,.46])
		if "--reverse" in OS.get_cmdline_user_args():line.reverse()
	elif which=="west_cut":
		line=[[-75.77,-16.7],[-75.3,-23.],[-74.95,-27.5],[-74.55,-33.],[-74.1,-38.]]
	elif which=="west_entry":
		line=[[-76.,-13.4]]
		for q:Array in JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_age/west_passage.json")):line.append([q[0],-q[1]])
		line.append([-74.6,-44.])
		if "--reverse" in OS.get_cmdline_user_args():line.reverse()
	elif which=="school":
		line=[[1.,-59.],[8.,-59.],[15.,-59.],[21.,-58.86],[28.,-57.91],[34.,-57.1]]
	elif which=="southeast":
		line=[[26.,64.98],[34.,63.95],[43.,62.81],[51.,61.75]]
	else:
		line=[[38.,74.65],[41.,74.68],[45.,74.67],[48.7,74.65],[54.,74.65]]
	var route:=PackedVector3Array()
	var space:=scene.get_world_3d().direct_space_state
	for pos in line:
		var estimate:=29. if which=="school" else 11.
		if which.begins_with("west_") or which.begins_with("east_") or which.begins_with("corner_"):estimate=5.5+.148*(100.-float(pos[1]))+.022*float(pos[0])
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(pos[0],estimate+1.9,pos[1]),Vector3(pos[0],estimate-4.,pos[1]),1))
		if not check("start_and_goal_support",not hit.is_empty(),pos):
			finish();return
		route.append(hit.position)
	var heading:Vector3=route[1]-route[0]
	var yaw:=atan2(-heading.x,-heading.z)
	var start:=route[0]
	route.remove_at(0)
	lesson._place_vehicle(lesson.mentor,start,yaw)
	lesson._place_vehicle(bike,start+Basis(Vector3.UP,yaw)*Vector3.BACK*3.6,yaw)
	lesson.demo.walker.board()
	await frames(65)
	bike.enter(game.actor)
	bike.automation=true
	lesson.step=lesson.Step.TO_YARD
	lesson.demo.start_second_ride()
	lesson.mentor.guide_to(route)
	await ride(which+"_both_arrive")
	finish()
