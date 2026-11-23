extends SceneTree
func _initialize()->void:call_deferred("take")
func take()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var folder:String=OS.get_cmdline_user_args()[-1]
	DirAccess.make_dir_recursive_absolute(folder)
	game.hud.hide()
	var camera:=Camera3D.new()
	root.add_child(camera)
	camera.current=true
	camera.fov=64.
	var rid:=root.get_viewport_rid()
	var gpu:Array[float]=[];var dt:Array[float]=[]
	RenderingServer.viewport_set_measure_render_time(rid,true)
	var prev:=Time.get_ticks_usec()
	for i in 326:
		var t:=clampf(float(i-26)/299.,0.,1.)
		var d:=sin(t*PI)
		camera.global_position=Vector3(-21.5-4.50*t,12.99,57.75+3.17*d)
		camera.look_at(Vector3(-24.13,12.65,64.79+d*.28),Vector3.UP)
		await RenderingServer.frame_post_draw
		var now:=Time.get_ticks_usec()
		if i>=26:
			dt.append((now-prev)/1000.)
			var ms:=RenderingServer.viewport_get_measured_render_time_gpu(rid)
			if ms>0.:gpu.append(ms)
		prev=now
	if gpu.is_empty():quit(3);return
	dt.sort();gpu.sort()
	var report:={"frames":dt.size(),"gpu_samples":gpu.size(),"gpu":RenderingServer.get_video_adapter_name(),"viewport":[root.size.x,root.size.y],"gpu_ms_p50":gpu[gpu.size()/2],"gpu_ms_p95":gpu[int(gpu.size()*.95)],"frame_ms_p50":dt[dt.size()/2],"frame_ms_p95":dt[int(dt.size()*.95)]}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	FileAccess.open(folder.path_join("shop_timing.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("SHOP_TIMING ",dt.size()," ",report.gpu_ms_p50," ",report.gpu_ms_p95)
	quit()
