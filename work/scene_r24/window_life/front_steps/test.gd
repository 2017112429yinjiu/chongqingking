extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay == null:
		await physics_frame
	var args := OS.get_cmdline_user_args()
	var study_dir: String = args[-1]
	var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(study_dir + "/measurements.json"))
	var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(study_dir + "/reopen.json"))
	var city: Node3D = game.get_node("City")
	var space: PhysicsDirectSpaceState3D = city.get_world_3d().direct_space_state
	var installation: Dictionary = game.scene_identity.get("market_steps", {})
	var failed := []
	var measurements := []
	for pair in [["COL_R24_MarketStairs_R24_step_stone",geometry.probes],["COL_R23_NanquUpperApron",source.cap_probes]]:
		var node := city.find_child(pair[0], true, false) as MeshInstance3D
		var body := node.get_node("CQ_StaticCollision") as StaticBody3D
		var saved := body.collision_layer
		body.collision_layer |= 16
		await physics_frame
		var max_error := 0.0
		for row in pair[1]:
			var point := Vector3(row[0],row[1],row[2])
			var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.24,point-Vector3.UP*.24,16))
			if hit.is_empty() or hit.collider != body:
				failed.append([pair[0],row,"no contact"])
			else:
				var error: float = absf(point.y-hit.position.y)
				max_error = maxf(error,max_error)
				if error>.003:
					failed.append([pair[0],row,error])
		measurements.append({"mesh":pair[0],"count":pair[1].size(),"largest_error_m":max_error})
		var finishes: Array = installation.get(pair[0],[])
		if not finishes.has("Market16_CutSandstone"):
			failed.append([pair[0],"scan missing"])
		body.collision_layer = saved
		await physics_frame
	var walker = game.explorer
	var routes := []
	for x in [-22.15,-21.40,-20.65]:
		var start := Vector3(x,8.0,80.75)
		var end := Vector3(x,8.85,76.85)
		var floor_hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP,start-Vector3.UP,1))
		if floor_hit.is_empty():
			failed.append([x,"missing lower sidewalk"])
			continue
		walker.begin_route_test(floor_hit.position+Vector3.UP*.035,end)
		for index in 18:await physics_frame
		var last: Vector3 = walker.body.global_position
		var metres:=0.0
		var max_step:=0.0
		var goals:=0
		for goal: Vector3 in [end,start]:
			walker.automation_axis=Vector2(0,-1)
			for tick in 360:
				walker.aim_route_test(goal)
				await physics_frame
				var current: Vector3 = walker.body.global_position
				var movement:=current-last
				metres+=Vector2(movement.x,movement.z).length()
				max_step=maxf(max_step,movement.length())
				last=current
				if Vector2(current.x-goal.x,current.z-goal.z).length()<.19:
					goals+=1
					break
		walker.end_route_test()
		routes.append({"x":x,"goals":goals,"metres":metres,"largest_step_m":max_step})
		if goals!=2 or max_step>.30:
			failed.append(routes.back())
	var report={"passed":failed.is_empty(),"failures":failed,"geometry":measurements,"routes":routes}
	var qa=preload("res://scripts/qa_context.gd")
	qa.decorate(report,game)
	var outdir: String=qa.directory("res://verification_r24/build16")
	DirAccess.make_dir_recursive_absolute(outdir)
	FileAccess.open(outdir+"/market_steps.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("MARKET16 ",report.passed," ",measurements," ",routes," ",failed)
	quit(0 if report.passed else 3)
