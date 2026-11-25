extends "../../scene_r24/outer_neighborhood/market_entry.gd"

func point(p: Array) -> Vector3:
	return Vector3(p[0],p[2],-float(p[1]))

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	var graphics:=DisplayServer.get_name()!="headless"
	if graphics:RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(32)
	var job=scene.gameplay.shancheng
	var money:int=scene.gameplay.earnings
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
	var courts: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	check("spawn_at_pickup",scene.explorer.body.global_position.distance_to(point(data.primary[0]))<.85)
	if graphics:
		recording=true
		record_tick()
	tap(KEY_E)
	await frames(18)
	check("pickup_with_E",job.stage==job.Stage.CARRYING)
	var delivery:=await WalkTest._walk(scene,data.primary.slice(1).map(point),"pickup_to_signed_receipt")
	check("walk_to_receiver",delivery["pass"],delivery)
	tap(KEY_E)
	await frames(24)
	check("receipt_with_E",job.stage==job.Stage.DELIVERED and scene.gameplay.earnings==money+6)
	var stop: Array=courts.courtyard_connections.school
	var points: Array=stop.slice(1).map(point)
	var school: Dictionary=courts.buildings.filter(func(b):return b.id=="jinma_classrooms")[0]
	points.append(Vector3(school.inside[0],school.floor+.05,-float(school.inside[1])))
	for tread: Array in school.stairs_to_library:
		points.append(point(tread))
	var visit:=await WalkTest._walk(scene,points,"receipt_to_upstairs_reading_room")
	check("walk_to_upstairs_library",visit["pass"],visit)
	check("on_reading_floor",absf(scene.explorer.body.global_position.y-float(school.floor)-3.48)<.22,str(scene.explorer.body.global_position))
	await frames(30)
	recording=false
	FileAccess.open(output.path_join("delivery_take.json"),FileAccess.WRITE).store_string(
		JSON.stringify({"checks":checks,"physics_hz":Engine.physics_ticks_per_second,"ticks_per_image":9,"images":saved_frames},"  "))
	quit(2 if ever_failed else 0)
