extends SceneTree
func _initialize()->void:call_deferred("study")
func study()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var folder:String=OS.get_cmdline_user_args()[-1]
	var oc:=OccluderInstance3D.new()
	oc.occluder=load(folder+"/interior_wall_faces.res")
	game.add_child(oc)
	var rid:=root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid,true)
	game.hud.hide()
	# Freeze residents and traffic so a pair has the same camera and pose.
	game.process_mode=Node.PROCESS_MODE_DISABLED
	var result=[]
	for view in ["r23_main_road","r24_main_tea_window","r24_west_pantry","r24_chess_table"]:
		game.explorer.go_to_view(view)
		for state in [false,true,false]:
			oc.visible=state
			root.use_occlusion_culling=state
			RenderingServer.viewport_set_use_occlusion_culling(rid,state)
			for idx in 18:await RenderingServer.frame_post_draw
			var times:Array[float]=[];var count=[];var shadows=[];var draws=[]
			for i in 18:
				await RenderingServer.frame_post_draw
				times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
				count.append(root.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME))
				shadows.append(root.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME))
				draws.append(root.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME))
			times.sort();count.sort();shadows.sort();draws.sort()
			var suffix=("%02d"%result.size())+("_on" if state else "_off")
			var frame:=root.get_texture().get_image()
			frame.save_png(folder+"/"+view+"_"+suffix+".png")
			result.append({"view":view,"culled":state,"gpu_p50":times[times.size()/2],"render_primitives":count[count.size()/2],"shadow_primitives":shadows[shadows.size()/2],"draws":draws[draws.size()/2]})
			FileAccess.open(folder+"/comparison.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
			print("ROOM15_OCC_SAMPLE ",result.back())
	quit()
