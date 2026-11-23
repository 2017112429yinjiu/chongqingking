extends SceneTree

func _initialize() -> void: call_deferred("record")

func record() -> void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null: await physics_frame
	var walker=main.explorer
	main.hud.hide()
	var folder=OS.get_cmdline_user_args()[-1]
	DirAccess.make_dir_recursive_absolute(folder)
	var foot_ray=PhysicsRayQueryParameters3D.create(Vector3(-35.2,10.5,76.9),Vector3(-35.2,7.,76.9),1)
	var ground=main.get_world_3d().direct_space_state.intersect_ray(foot_ray)
	if ground.is_empty():
		quit(2)
		return
	var goal=Vector3(-26.8,8.9,76.65)
	walker.begin_route_test(ground.position+Vector3.UP*.04,goal)
	for settle in 15:await physics_frame
	var initial: Vector3=walker.body.global_position
	var last: Vector3=initial
	var frames: Array=[]
	var max_jump:=0.
	var saved:=0
	var reached:=false
	for index in range(240):
		# Walk east along the frontage, with the player's gaze angled toward the market.
		var pos:Vector3=walker.body.global_position
		var gaze:=Vector3(pos.x+5.,pos.y,pos.z-2.15)
		walker.aim_route_test(gaze)
		walker.automation_axis=Vector2(.37,-.93)
		await physics_frame
		pos=walker.body.global_position
		max_jump=maxf(max_jump,last.distance_to(pos));last=pos
		if index%4==0:
			await RenderingServer.frame_post_draw
			var frame=root.get_texture().get_image()
			if frame.is_empty() or frame.save_jpg(folder.path_join("walk_%03d.jpg"%saved),.91)!=OK:
				quit(3)
				return
			frames.append([index,pos.x,pos.y,pos.z])
			saved+=1
		if pos.x>=goal.x:
			reached=true
			break
	walker.end_route_test()
	var report={"reached":reached,"captured":saved,"metres":last.distance_to(initial),"max_physics_step_m":max_jump,"samples":frames}
	FileAccess.open(folder.path_join("continuous.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("CQ_WALK_TAKE ",reached," ",saved," ",last.distance_to(initial)," ",max_jump)
	quit(0 if reached and saved>=15 and max_jump<.50 else 4)

