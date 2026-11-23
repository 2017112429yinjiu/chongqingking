extends SceneTree

func _initialize() -> void: call_deferred("measure")

func measure() -> void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var walker=game.explorer
	var near_point:=Vector3(-70.65,14.45,29.8)
	var far_point:=Vector3(-69.2,16.62,16.8)
	var ground=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(near_point+Vector3.UP*2.,near_point-Vector3.UP*2.,1))
	if ground.is_empty():quit(2);return
	walker.begin_route_test(ground.position+Vector3.UP*.04,far_point)
	for i in 20:await RenderingServer.frame_post_draw
	var gpu:Array[float]=[]
	var intervals:Array[float]=[]
	var rid:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid,true)
	var previous:=Time.get_ticks_usec()
	var end_time:=previous+16_000_000
	var distance:=0.
	var last:Vector3=walker.body.global_position
	var target:=far_point
	var crossings:=0
	while Time.get_ticks_usec()<end_time:
		walker.aim_route_test(target)
		walker.automation_axis=Vector2(0,-1)
		await RenderingServer.frame_post_draw
		var now:=Time.get_ticks_usec()
		var value:=RenderingServer.viewport_get_measured_render_time_gpu(rid)
		if value>0.:gpu.append(value)
		intervals.append((now-previous)/1000.)
		previous=now
		var position:Vector3=walker.body.global_position
		distance+=Vector2(position.x-last.x,position.z-last.z).length()
		last=position
		if Vector2(position.x-target.x,position.z-target.z).length()<.45:
			target=near_point if target==far_point else far_point
			crossings+=1
	walker.end_route_test()
	gpu.sort();intervals.sort()
	if gpu.is_empty():quit(3);return
	var result={"window_size":[root.size.x,root.size.y],"metres":distance,"reversals":crossings,"drawn_frames":intervals.size(),"gpu_samples":gpu.size(),"gpu_p50_ms":gpu[gpu.size()/2],"gpu_p95_ms":gpu[int(gpu.size()*.95)],"frame_interval_p50_ms":intervals[intervals.size()/2],"frame_interval_p95_ms":intervals[int(intervals.size()*.95)],"gpu":RenderingServer.get_video_adapter_name()}
	preload("res://scripts/qa_context.gd").decorate(result,game)
	var dir=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir.path_join("window_walk.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("CQ_WINDOW_WALK ",distance," ",crossings," ",intervals.size()," ",result.frame_interval_p50_ms)
	quit(0 if crossings>0 else 4)

