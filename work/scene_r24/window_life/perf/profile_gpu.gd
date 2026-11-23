extends SceneTree
func _initialize()->void:call_deferred("measure")
func measure()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var folder:String=OS.get_cmdline_user_args()[-1]
	var rid:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid,true)
	var sun:DirectionalLight3D=game.find_children("*","DirectionalLight3D",true,false)[0]
	var env:Environment=game.get_world_3d().environment
	var original_range:=sun.directional_shadow_max_distance
	var original_fuzz:=sun.light_angular_distance
	var original_aa:=root.msaa_3d
	var tree_meshes:Dictionary={}
	for mesh:MeshInstance3D in game.get_node("City").find_children("*","MeshInstance3D",true,false):
		if not mesh.mesh:continue
		var n=str(mesh.name)+" "+mesh.mesh.resource_name
		if "Planted_tree_" in n or "Canopy_" in n or "N13_Greenery" in n:tree_meshes[mesh]=mesh.cast_shadow
	game.hud.hide();game.process_mode=Node.PROCESS_MODE_DISABLED
	var result=[]
	for view in ["r23_main_road","r24_main_tea_window"]:
		game.explorer.go_to_view(view)
		for mode in ["baseline","no_tree_shadow","range_85","medium_filter","soft_sun_08","no_ssil","aa2","all_shadow_off","baseline_end"]:
			sun.directional_shadow_max_distance=85. if mode=="range_85" else original_range
			sun.light_angular_distance=.8 if mode=="soft_sun_08" else original_fuzz
			sun.shadow_enabled=mode!="all_shadow_off"
			env.ssil_enabled=mode!="no_ssil"
			root.msaa_3d=Viewport.MSAA_2X if mode=="aa2" else original_aa
			for tree in tree_meshes:
				tree.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if mode=="no_tree_shadow" else tree_meshes[tree]
			RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM if mode=="medium_filter" else RenderingServer.SHADOW_QUALITY_SOFT_HIGH)
			for i in 12:await RenderingServer.frame_post_draw
			var times:Array[float]=[]
			for i in 14:
				await RenderingServer.frame_post_draw
				times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
			times.sort()
			var tris=root.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)
			var main_tris=root.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)
			result.append({"view":view,"mode":mode,"gpu_p50":times[7],"shadow_triangles":tris,"visible_triangles":main_tris,"caster_count":tree_meshes.size()})
			root.get_texture().get_image().save_png(folder+"/probe_"+view+"_"+mode+".png")
			FileAccess.open(folder+"/stage_times.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
			print("RENDER_STAGE ",result.back())
	quit()
