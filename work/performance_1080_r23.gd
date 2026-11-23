extends SceneTree

func _initialize() -> void:
	call_deferred("measure")

func measure() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	main.hud.visible=false
	var target:=SubViewport.new()
	target.size=Vector2i(1920,1080)
	target.world_3d=main.get_world_3d()
	target.msaa_3d=root.msaa_3d
	target.screen_space_aa=root.screen_space_aa
	var aa_trial:bool="--post-aa-trial" in OS.get_cmdline_user_args()
	if aa_trial:
		target.msaa_3d=Viewport.MSAA_DISABLED
		target.screen_space_aa=Viewport.SCREEN_SPACE_AA_FXAA
	target.use_taa=root.use_taa
	target.scaling_3d_scale=1.
	target.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	main.add_child(target)
	var camera:=Camera3D.new()
	target.add_child(camera)
	camera.far=main.explorer.camera.far
	camera.make_current()
	root.disable_3d=true
	var display:=TextureRect.new()
	root.add_child(display)
	display.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	display.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	display.texture=target.get_texture()
	var viewport:=target.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(viewport,true)
	var rows:Array=[]
	var directory:String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(directory)
	var names:=PackedStringArray(["r23_main_road","r23_shop_window","r23_street_support"])
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--perf-views="):names=arg.trim_prefix("--perf-views=").split(",",false)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--perf-camera-file="):
			var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(arg.trim_prefix("--perf-camera-file=")))
			for key in names:
				if not main.explorer._views.has(key) and plan.views.has(key):
					var info: Dictionary=plan.views[key]
					main.explorer._views[key]={"position":Vector3(info.position[0],info.position[1],info.position[2]),"target":Vector3(info.target[0],info.target[1],info.target[2]),"fov":info.fov}
	for name_of_view:String in names:
		if not main.explorer._views.has(name_of_view):
			push_error("Unknown GPU review camera: "+name_of_view)
			quit(2)
			return
		main.explorer.go_to_view(name_of_view)
		camera.global_transform=main.explorer.camera.global_transform
		camera.fov=main.explorer.camera.fov
		for i in 90:await RenderingServer.frame_post_draw
		var gpu:Array[float]=[]
		var intervals:Array[float]=[]
		var previous:=Time.get_ticks_usec()
		for i in 240:
			await RenderingServer.frame_post_draw
			var now:=Time.get_ticks_usec()
			gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(viewport))
			intervals.append((now-previous)/1000.)
			previous=now
		gpu.sort()
		intervals.sort()
		if gpu[0]<=0. or target.get_texture().get_size()!=Vector2(1920,1080):
			push_error("Missing GPU timestamps or incorrect target size")
			quit(2)
			return
		var frame:=target.get_texture().get_image()
		if frame==null or frame.is_empty() or frame.get_size()!=Vector2i(1920,1080):
			push_error("Full-resolution framebuffer readback failed")
			quit(2)
			return
		var full_frame_path:=directory+"/1080_"+name_of_view+".png"
		if frame.save_png(full_frame_path)!=OK:
			quit(2)
			return
		rows.append({"view":name_of_view,"position":str(camera.global_position),"fov":camera.fov,
			"samples":gpu.size(),"gpu_p50_ms":gpu[120],"gpu_p95_ms":gpu[228],
			"readback_sha256":FileAccess.get_sha256(full_frame_path),
			"engine_video_memory_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED),
			"engine_texture_memory_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),
			"frame_interval_p95_ms":intervals[228]})
	var report:Dictionary={"gpu":RenderingServer.get_video_adapter_name(),"framebuffer":[1920,1080],"post_aa_trial":aa_trial,
		"msaa_3d":target.msaa_3d,"screen_space_aa":target.screen_space_aa,
		"scale":target.scaling_3d_scale,"native_window_3d_disabled":root.disable_3d,"views":rows}
	preload("res://scripts/qa_context.gd").decorate(report,main)
	FileAccess.open(directory+"/native_1080.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	quit()
