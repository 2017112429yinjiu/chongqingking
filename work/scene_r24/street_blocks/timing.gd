extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(36)
	if DisplayServer.get_name()=="headless":
		quit(3)
		return
	var geo: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://source_data/geo_layout.json"))
	var path: Array=geo.paths.filter(func(entry):return int(entry.id)==734116601)[0].points
	var points: Array=[["window",path[4],[-207.,181.]],["bend",path[7],[-228.,160.]],["handoff",path[34],path[32]]]
	var vp:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vp,true)
	await create_timer(8.).timeout
	var rows: Array=[]
	for site: Array in points:
		var foot:=terrain(site[1])+Vector3.UP*.045
		var target:=terrain(site[2])+Vector3.UP*1.6
		scene.explorer.set_walk_origin(foot,target)
		await frames(65)
		var gpu: Array[float]=[]
		var wall: Array[float]=[]
		var last:=Time.get_ticks_usec()
		for i in 150:
			await process_frame
			var now:=Time.get_ticks_usec()
			wall.append((now-last)*.001)
			gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
			last=now
		wall.sort();gpu.sort()
		rows.append({"view":site[0],"samples":gpu.size(),"gpu_p50_ms":gpu[75],"gpu_p95_ms":gpu[142],"wall_p95_ms":wall[142]})
	var result:={"engine":Engine.get_version_info().string,"adapter":RenderingServer.get_video_adapter_name(),"window":str(DisplayServer.window_get_size()),"viewport":str(root.get_texture().get_size()),"render_method":RenderingServer.get_current_rendering_method(),"views":rows}
	FileAccess.open(output.path_join("timing.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	quit(0 if rows.all(func(s):return s.gpu_p50_ms>0.) else 2)
