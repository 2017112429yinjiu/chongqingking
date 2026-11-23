extends RefCounted
static func run(main: Node3D) -> void:
	if DisplayServer.get_name()=="headless":
		main.get_tree().quit(3)
		return
	var results: Array = []
	var measure_gpu: bool="--viewport-gpu" in OS.get_cmdline_user_args()
	var viewport: RID=main.get_viewport().get_viewport_rid()
	if measure_gpu:
		RenderingServer.viewport_set_measure_render_time(viewport,true)
	var views: Array=["street_entry","residential_entry","roofscape","r18_workstation","r18_face","r18_rider_active"]
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--perf-views="):views=Array(arg.trim_prefix("--perf-views=").split(","))
	for view in views:
		if view=="r18_rider_active":
			var vehicle: Node3D=main.gameplay.scooter
			main.explorer.set_mode(true)
			vehicle.enter(main.explorer)
			vehicle.automation=true
			vehicle.test_throttle=0.0
		else:main.explorer.go_to_view(view)
		for frame in range(90):
			await main.get_tree().process_frame
		var samples: Array[float] = []
		var gpu_samples: Array[float]=[]
		var tick: int = Time.get_ticks_usec()
		for frame in range(240):
			await main.get_tree().process_frame
			var now: int = Time.get_ticks_usec()
			samples.append(float(now-tick)/1000.0)
			if measure_gpu:
				gpu_samples.append(RenderingServer.viewport_get_measured_render_time_gpu(viewport))
			tick=now
		samples.sort()
		var total: float = 0
		for ms in samples: total+=ms
		results.append({"view":view,"samples":samples.size(),"mean_ms":total/samples.size(),"p50_ms":samples[120],"p95_ms":samples[228],"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"static_memory_bytes":Performance.get_monitor(Performance.MEMORY_STATIC)})
		if measure_gpu:
			gpu_samples.sort()
			results.back()["viewport_gpu_p50_ms"]=gpu_samples[120]
			results.back()["viewport_gpu_p95_ms"]=gpu_samples[228]
			results.back()["viewport_gpu_positive_count"]=gpu_samples.filter(func(v):return v>0.).size()
	var report: Dictionary = {"engine":Engine.get_version_info().string,"gpu":RenderingServer.get_video_adapter_name(),"renderer":RenderingServer.get_current_rendering_method(),"window_size":str(main.get_viewport().get_visible_rect().size),"vsync":DisplayServer.window_get_vsync_mode(),"views":results,"scene_sha256":FileAccess.get_sha256("res://assets/chongqing_district.glb"),"character_sha256":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),"note":"Desktop frame intervals for the listed stationary viewpoints. Each view settles for 90 frames then records 240 intervals. Includes scene rendering, gameplay and OS scheduling."}
	report["character_import_sha256"]=FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import")
	if measure_gpu:
		report["window_pixels"]=str(DisplayServer.window_get_size())
		report["viewport_texture_pixels"]=str(main.get_viewport().get_texture().get_size())
		report["gpu_timing"]="RenderingServer GPU timestamps for this viewport, sampled once per frame. Desktop frame intervals are reported separately."
		RenderingServer.viewport_set_measure_render_time(viewport,false)
	report["rider_sha256"]=FileAccess.get_sha256("res://assets/characters/rider_r18.glb")
	report["vehicle_sha256"]=FileAccess.get_sha256("res://assets/vehicles/scooter_r18.glb")
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var output: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	FileAccess.open(output+"/performance.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("R18_PERFORMANCE ",JSON.stringify(report))
	main.get_tree().quit()
