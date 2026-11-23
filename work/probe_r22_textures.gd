extends SceneTree

func _initialize() -> void:
	call_deferred("measure")

func measure() -> void:
	var plan:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--texture-plan="):plan=arg.trim_prefix("--texture-plan=")
	var recipes:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(plan))
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	main.explorer.go_to_view("central_steps")
	for i in 90:await RenderingServer.frame_post_draw
	var texture_bytes:=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
	var bytes:=0
	var data:Array=[]
	for item:Dictionary in recipes.sources:
		var path:="res://"+str(item.path).trim_suffix(".import")
		var was_loaded:=ResourceLoader.has_cached(path)
		var texture:=load(path) as Texture2D
		var img:=texture.get_image()
		if img==null or img.is_empty():
			push_error("Texture readback failed at "+path)
			quit(2)
			return
		var amount:=img.get_data_size()
		if was_loaded:bytes+=amount
		data.append({"path":path,"already_loaded":was_loaded,"format":img.get_format(),
			"mips":img.get_mipmap_count(),"width":img.get_width(),"height":img.get_height(),"bytes":amount})
	var report:Dictionary={"scene_texture_bytes_before_readback":texture_bytes,"cached_scan_bytes":bytes,"maps":data,
		"gpu":RenderingServer.get_video_adapter_name(),"scope":"Game opened at central steps. Per-map storage includes mipmaps and uses imported image format."}
	var out:String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(out)
	FileAccess.open(out+"/texture_probe.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	quit()
