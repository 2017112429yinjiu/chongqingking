extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(25)
	game=scene.gameplay
	if DisplayServer.get_name()=="headless" or not game.lunch.can_offer():quit(3);return
	var vp:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vp,true)
	game.actor.camera.look_at(game.lunch.counters[1]+Vector3.UP*.15)
	game.actor._sync_angles()
	# Let the delayed district layers and shader compilation finish before either sample.
	await create_timer(23.0).timeout
	var rows:Array=[]
	for name_:String in ["counter","three_ready"]:
		if name_=="three_ready":
			tap(KEY_G)
			tap(KEY_E)
			while game.lunch.active and game.lunch.elapsed<22.1:await physics_frame
			if not game.lunch.active:quit(2);return
		for warm in 50:await process_frame
		var timings:Array[float]=[]
		var walls:Array[float]=[]
		var last:=Time.get_ticks_usec()
		for frame in 120:
			await process_frame
			var now:=Time.get_ticks_usec()
			walls.append((now-last)/1000.)
			last=now
			timings.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
		timings.sort()
		walls.sort()
		rows.append({"view":name_,"gpu_ms_p50":timings[60],"gpu_ms_p95":timings[114],"wall_ms_p95":walls[114],"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"samples":120})
	var result:={"gpu":RenderingServer.get_video_adapter_name(),"window":str(DisplayServer.window_get_size()),"viewport":str(root.get_texture().get_size()),"measurements":rows}
	FileAccess.open(output.path_join("timing.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"\t"))
	quit(0 if rows[1].gpu_ms_p50>0. else 2)
