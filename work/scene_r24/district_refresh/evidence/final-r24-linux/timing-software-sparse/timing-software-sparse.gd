extends "/workspace/chongqing-refresh/work/scene_r24/day_one/verify.gd"

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay: await physics_frame
	await frames(30)
	game=scene.gameplay
	var rows: Array=[]
	var viewpoints: Array=[
		["switchback", Vector3(-84.84,17.12,9.90), Vector3(-84.80,21.6,17.36)],
		["crossing", Vector3(-75.85,23.92,14.4), Vector3(-65.8,25.0,14.36)],
		["301", Vector3(-61.5,22.90,14.36), game.passage.DOOR],
	]
	for view: Array in viewpoints:
		game.actor.begin_route_test(view[1]+Vector3.UP*.055, view[2])
		await frames(12)
		RenderingServer.render_loop_enabled=true
		for warmup in 4: await RenderingServer.frame_post_draw
		var last:=Time.get_ticks_usec()
		var wall: Array[float]=[]
		for sample in 8:
			await RenderingServer.frame_post_draw
			var now:=Time.get_ticks_usec()
			wall.append((now-last)*.001)
			last=now
		RenderingServer.render_loop_enabled=false
		var sorted:=wall.duplicate()
		sorted.sort()
		rows.append({"view":view[0],"samples":wall.size(),"wall_frame_intervals_ms":wall,"median_ms":(sorted[3]+sorted[4])*.5})
		var result: Dictionary={"device":RenderingServer.get_video_adapter_name(),"window":str(DisplayServer.window_get_size()),"viewport":str(root.get_texture().get_size()),"views":rows,"warm_frames_per_view":4}
		FileAccess.open(output.path_join("sparse-timing.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"\t"))
		print("CQ_SPARSE_SOFTWARE_TIMING ",JSON.stringify(rows[-1]))
	quit()
