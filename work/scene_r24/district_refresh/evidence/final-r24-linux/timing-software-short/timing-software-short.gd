extends "/workspace/chongqing-refresh/work/scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(30)
	game=scene.gameplay
	if DisplayServer.get_name()=="headless":quit(3);return
	var vp:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vp,true)
	await create_timer(20.).timeout
	var rows:Array=[]
	for view:Array in [
		["switchback",Vector3(-84.84,17.12,9.90),Vector3(-84.80,21.6,17.36)],
		["crossing",Vector3(-75.85,23.92,14.4),Vector3(-65.8,25.0,14.36)],
		["301",Vector3(-61.5,22.90,14.36),game.passage.DOOR]]:
		game.actor.begin_route_test(view[1]+Vector3.UP*.055,view[2])
		await frames(12)
		var gpu:Array[float]=[]
		var wall:Array[float]=[]
		var last:=Time.get_ticks_usec()
		for i in 150:
			await process_frame
			var now:=Time.get_ticks_usec()
			gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
			wall.append((now-last)*.001)
			last=now
		gpu.sort();wall.sort()
		rows.append({"view":view[0],"samples":24,"gpu_p50_ms":gpu[12],"gpu_p95_ms":gpu[22],"wall_p95_ms":wall[22]})
		print("CQ_SOFTWARE_SHORT_TIMING ",JSON.stringify(rows[-1]))
	var result:={"device":RenderingServer.get_video_adapter_name(),"window":str(DisplayServer.window_get_size()),"viewport":str(root.get_texture().get_size()),"views":rows}
	FileAccess.open(output.path_join("timing.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"\t"))
	quit(0 if rows[1].gpu_p50_ms>0. else 2)
