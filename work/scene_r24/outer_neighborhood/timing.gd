extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in 1400:
		if scene.get("gameplay"):break
		await physics_frame
	if DisplayServer.get_name()=="headless" or not scene.get("gameplay"):
		quit(2)
		return
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary=layout.plots[1]
	assert(p.name=="照相巷便民市场")
	var f: float=-p.depth/2.0
	var c: Dictionary=p.court
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.make_current()
	camera.fov=71
	var vp:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vp,true)
	var result: Array=[]
	for pair: Array in [
		["front",world(p,-8.4,f-6.1,1.43),world(p,p.door_u+1,f+.4,1.52)],
		["produce_counter",world(p,p.door_u-.24,f+.24,1.61),world(p,p.door_u+3.27,f+1.85,1.24)],
		["upper_court",world(p,p.door_u,-f+.45,1.66),world(p,c.stair_u*.35,c.landing_v+1.1,2.20)]]:
		camera.global_position=pair[1]
		camera.look_at(pair[2])
		for i in 18: await process_frame
		var gpu: Array[float]=[]
		var wall: Array[float]=[]
		var last:=Time.get_ticks_usec()
		for i in 90:
			await process_frame
			var now:=Time.get_ticks_usec()
			wall.append((now-last)*.001)
			last=now
			gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
		wall.sort();gpu.sort()
		result.append({"view":pair[0],"frames":gpu.size(),"gpu_p50_ms":gpu[45],"gpu_p95_ms":gpu[85],"wall_p95_ms":wall[85]})
	FileAccess.open(output.path_join("timing.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"device":RenderingServer.get_video_adapter_name(),"window":str(DisplayServer.window_get_size()),
		"viewport":str(root.get_texture().get_size()),"renderer":RenderingServer.get_current_rendering_method(),"views":result},"  "))
	quit(0 if result[0].gpu_p50_ms>0 else 2)
