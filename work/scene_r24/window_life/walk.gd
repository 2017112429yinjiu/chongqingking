extends SceneTree
func _initialize()->void:
	call_deferred("walk")

func walk()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var walker=game.explorer
	var args:=OS.get_cmdline_user_args()
	var folder:String=args[-1]
	var perf:bool="--timing" in args
	DirAccess.make_dir_recursive_absolute(folder)
	game.hud.hide()
	var start:=Vector3(-37.65,10.,76.45)
	var end:=Vector3(-25.2,10.,76.45)
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP*2.,start-Vector3.UP*4.,1))
	if hit.is_empty():quit(2);return
	walker.begin_route_test(hit.position+Vector3.UP*.03,end)
	for i in 12:await physics_frame
	var last:Vector3=walker.body.global_position
	var largest:=0.;var distance:=0.;var timeline=[];var reached:=false;var turns:=0
	var goal:=end;var attempts:=0;var interval:Array[float]=[];var gpu:Array[float]=[]
	var rid:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid,perf)
	var begin:=Time.get_ticks_usec();var previous:=begin
	while (Time.get_ticks_usec()-begin<16000000 if perf else attempts<660):
		var pos:Vector3=walker.body.global_position
		var along:=smoothstep(-33.5,-27.5,pos.x)
		var focus:Vector3=Vector3(-31.38,13.45,72.6).lerp(Vector3(-28.15,13.74,72.22),along)
		walker.camera.look_at(focus,Vector3.UP)
		walker._sync_angles()
		var forward:Vector3=-walker.camera.global_basis.z;forward.y=0;forward=forward.normalized()
		var delta:Vector3=goal-pos;delta.y=0.
		if delta.length()<.22:
			reached=true;turns+=1
			if not perf:break
			goal=start if goal==end else end
			delta=goal-pos;delta.y=0.
		var dir:=delta.normalized()
		walker.automation_axis=Vector2(dir.dot(forward.cross(Vector3.UP)),-dir.dot(forward))*.7
		if perf:
			await RenderingServer.frame_post_draw
			var now:=Time.get_ticks_usec()
			interval.append((now-previous)/1000.);previous=now
			var value:=RenderingServer.viewport_get_measured_render_time_gpu(rid)
			if value>0:gpu.append(value)
		else:await physics_frame
		var current:Vector3=walker.body.global_position
		largest=maxf(largest,current.distance_to(last));distance+=Vector2(current.x-last.x,current.z-last.z).length();last=current
		if not perf and attempts%6==0:
			await RenderingServer.frame_post_draw
			var image=root.get_texture().get_image()
			if image.is_empty() or image.save_jpg(folder.path_join("frame_%03d.jpg"%timeline.size()),.91)!=OK:quit(3);return
			timeline.append([attempts,current.x,current.y,current.z])
		attempts+=1
	walker.end_route_test()
	var report={"passed":reached and (perf or largest<.30),"frames":timeline,"metres":distance,"reversals_or_arrivals":turns,"max_update_m":largest,"stop":[last.x,last.y,last.z],"window":[root.size.x,root.size.y]}
	if perf:
		interval.sort();gpu.sort()
		if gpu.is_empty() or interval.is_empty():quit(4);return
		report.merge({"drawn_frames":interval.size(),"gpu":RenderingServer.get_video_adapter_name(),"frame_p50":interval[interval.size()/2],"frame_p95":interval[int(interval.size()*.95)],"gpu_p50":gpu[gpu.size()/2],"gpu_p95":gpu[int(gpu.size()*.95)]})
	preload("res://scripts/qa_context.gd").decorate(report,game)
	FileAccess.open(folder+"/walk.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("ROOM15_WALK ",report.passed," ",distance," ",turns," ",last," ",attempts)
	quit(0 if report.passed else 5)
