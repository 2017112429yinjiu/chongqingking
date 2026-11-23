extends SceneTree

func _initialize()->void:
	call_deferred("record")

func record()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var flags:=OS.get_cmdline_user_args()
	var folder:String=flags[-1]
	var timing:bool="--timing" in flags
	DirAccess.make_dir_recursive_absolute(folder)
	game.hud.hide()
	var walker=game.explorer
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/lane_connection_r24/layout.json"))
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	var start:=Vector3(26.65,22.64,-8.03)
	var goals:Array[Vector3]=[Vector3(27.22,23.18,-10.61),Vector3(27.97,23.51,-13.55)]
	for i in range(plan.steps.size()-1,-1,-1):
		var centre:=Vector3.ZERO
		for corner in plan.steps[i]:centre+=Vector3(corner[0],0,-corner[1])*.25
		centre.y=plan.height-(plan.steps.size()-1-i)*.169265
		goals.append(centre)
	goals.append(Vector3(33.54,22.61,-7.0))
	var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP,start-Vector3.UP,1))
	if hit.is_empty():quit(2);return
	walker.begin_route_test(hit.position+Vector3.UP*.035,goals[0])
	for i in 15:await physics_frame
	var focus:=Vector3(28.5,23.6,-13.75)
	var forward_focus:=focus
	var frame:=0
	var frames:Array=[]
	var stage:=0
	var passes:=0
	var last:Vector3=walker.body.global_position
	var travel:=0.;var largest:=0.
	var elapsed:Array[float]=[];var gpu:Array[float]=[]
	var rid:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid,timing)
	var previous:=Time.get_ticks_usec()
	var began:=previous
	while (Time.get_ticks_usec()-began<16000000 if timing else frame<750):
		var pos:Vector3=walker.body.global_position
		var goal:=goals[stage]
		var delta:=goal-pos
		delta.y=0.
		if delta.length()<.17:
			stage+=1
			if stage==goals.size():
				passes+=1
				if not timing:break
				goals.reverse()
				goals.pop_front()
				goals.append(start)
				start=goal
				stage=0
			continue
		var desired:=delta.normalized()
		if stage<2 and passes==0:
			forward_focus=Vector3(29.03,23.84,-13.60)
		else:
			var future:=goals[mini(stage+1,goals.size()-1)]
			forward_focus=Vector3(pos.x+desired.x*2.8,future.y+.30,pos.z+desired.z*2.8)
		focus=focus.lerp(forward_focus,.059)
		walker.camera.look_at(focus,Vector3.UP)
		walker._sync_angles()
		var forward:Vector3=-walker.camera.global_basis.z
		forward.y=0;forward=forward.normalized()
		walker.automation_axis=Vector2(desired.dot(forward.cross(Vector3.UP)),-desired.dot(forward))*.67
		if timing:
			await RenderingServer.frame_post_draw
			var now:=Time.get_ticks_usec()
			elapsed.append(float(now-previous)/1000.);previous=now
			var g:=RenderingServer.viewport_get_measured_render_time_gpu(rid)
			if g>0:gpu.append(g)
		else:await physics_frame
		var cur:Vector3=walker.body.global_position
		travel+=Vector2(cur.x-last.x,cur.z-last.z).length();largest=maxf(largest,cur.distance_to(last));last=cur
		if not timing and frame%5==0:
			await RenderingServer.frame_post_draw
			var im:=root.get_texture().get_image()
			if im.is_empty() or im.save_jpg(folder.path_join("frame_%03d.jpg"%frames.size()),.94)!=OK:quit(3);return
			frames.append([frame,cur.x,cur.y,cur.z,stage])
		frame+=1
	walker.end_route_test()
	var result:={"passed":passes>0 and (timing or largest<.27),"arrivals":passes,"subgoals":stage,"total_subgoals":goals.size(),"metres":travel,"max_update_m":largest,"path":frames,"viewport":[root.size.x,root.size.y],"gpu":RenderingServer.get_video_adapter_name()}
	if timing:
		if elapsed.is_empty() or gpu.is_empty():quit(4);return
		elapsed.sort();gpu.sort()
		result.merge({"rendered_frames":elapsed.size(),"gpu_ms_p50":gpu[gpu.size()/2],"gpu_ms_p95":gpu[int(gpu.size()*.95)],"frame_ms_p50":elapsed[elapsed.size()/2],"frame_ms_p95":elapsed[int(elapsed.size()*.95)]})
	preload("res://scripts/qa_context.gd").decorate(result,game)
	FileAccess.open(folder.path_join("walk.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("EAST17_WALK ",result.passed," ",travel," ",passes," ",stage," ",frames.size())
	quit(0 if result.passed else 5)
