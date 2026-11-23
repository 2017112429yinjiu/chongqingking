extends SceneTree

func _initialize() -> void:
	call_deferred("test")

func test() -> void:
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null or game.street_block.tracks.is_empty():await physics_frame
	var result: Dictionary=game.scene_identity["street_finish_r24"]
	var passed: bool=result.local_frame and result.missing.is_empty() and result.retired==3 and result.donors>=4
	var walker = game.explorer
	var records: Array = []
	var routes := [
		[Vector3(-73.65,15.0,27.),Vector3(-73.0,15.6,23.),Vector3(-72.73,16.1,18.),Vector3(-73.1,16.8,13.)],
		[Vector3(-19.3,16.4,26.),Vector3(-19.0,16.9,21.),Vector3(-18.5,17.3,17.),Vector3(-18.5,18.1,11.)],
		[Vector3(8.6,11.4,61.4),Vector3(4.7,11.5,59.1),Vector3(-.2,11.75,57.8),Vector3(-5.0,12.,56.35)],
		[Vector3(-18.6,19.85,.47),Vector3(-20.04,19.85,.47),Vector3(-21.6,20.5,.32),Vector3(-23.2,20.54,.20)]]
	for path in routes:
		var first: Vector3=path[0]
		var floor_ray := PhysicsRayQueryParameters3D.create(first+Vector3.UP*1.6,first-Vector3.UP*2.,1)
		var floor_hit: Dictionary=game.get_world_3d().direct_space_state.intersect_ray(floor_ray)
		if floor_hit.is_empty():
			records.append({"floor":false})
			passed=false
			continue
		walker.begin_route_test(floor_hit.position+Vector3.UP*.035,path[1])
		for k in 18:await physics_frame
		var prev: Vector3=walker.body.global_position
		var distance:=0.
		var largest:=0.
		var waypoints: Array=[]
		var end_to_end: Array=path.slice(1)
		end_to_end.append_array([path[2],path[1],path[0]])
		for goal: Vector3 in end_to_end:
			walker.automation_axis=Vector2(0,-1)
			var ok:=false
			for tick in 360:
				walker.aim_route_test(goal)
				await physics_frame
				var pos: Vector3=walker.body.global_position
				distance+=Vector2(pos.x-prev.x,pos.z-prev.z).length()
				largest=maxf(largest,prev.distance_to(pos))
				prev=pos
				if Vector2(pos.x-goal.x,pos.z-goal.z).length()<.30:
					ok=true
					break
			waypoints.append({"ok":ok,"pos":[prev.x,prev.y,prev.z]})
			if not ok:
				var blockers: Array=[]
				for k in walker.body.get_slide_collision_count():
					blockers.append(str(walker.body.get_slide_collision(k).get_collider().get_parent().name))
				waypoints.back()["contacts"]=blockers
				passed=false
				break
		walker.end_route_test()
		passed=passed and largest<.7
		records.append({"metres":distance,"max_step":largest,"goals":waypoints})
	var data := {"passed":passed,"routes":records,"install":result,"engine":Engine.get_version_info().string}
	preload("res://scripts/qa_context.gd").decorate(data,game)
	var output=ProjectSettings.globalize_path(preload("res://scripts/qa_context.gd").directory("res://verification_r24/build17b/city_frame"))
	DirAccess.make_dir_recursive_absolute(output)
	FileAccess.open(output.path_join("seam_walk.json"),FileAccess.WRITE).store_string(JSON.stringify(data,"  "))
	print("CQ_SEAM_WALK ",JSON.stringify(data))
	quit(0 if passed else 3)

