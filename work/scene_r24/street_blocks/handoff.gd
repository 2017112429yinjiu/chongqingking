extends "../../scene_r24/outer_neighborhood/survey.gd"

func vec(q: Array) -> Vector3:return Vector3(q[0],q[2],-q[1])

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(26)
	var g=scene.gameplay
	var job=g.shancheng
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
	var graph:=DisplayServer.get_name()!="headless"
	if graph:RenderingServer.render_loop_enabled=false
	var feet:=Vector3.INF
	for route: String in ["primary","branch"]:
		var points: Array=data[route].map(func(q):return vec(q))
		if not check(route+"_starts_at_shelf",scene.explorer.body.global_position.distance_to(points[0])<.85):break
		var money:int=g.earnings
		check(route+"_pickup",g.manager.interact() and job.stage==job.Stage.CARRYING)
		if graph:await shot(route+"_pickup",points[0]+Vector3.UP*1.6,job.sender.global_position)
		var trip:=await WalkTest._walk(scene,points.slice(1),route+"_walk")
		check(route+"_walk",trip["pass"],trip)
		if not trip["pass"]:break
		check(route+"_drop",g.manager.interact() and job.stage==job.Stage.DELIVERED and g.earnings==money+6)
		check(route+"_one_payment",not g.manager.interact() and g.earnings==money+6)
		if graph:await shot(route+"_drop",points.back()+Vector3.UP*1.60,job.receiver.global_position)
		points.reverse()
		var back:=await WalkTest._walk(scene,points.slice(1),route+"_return")
		check(route+"_return",back["pass"],back)
		if not back["pass"]:break
	FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
