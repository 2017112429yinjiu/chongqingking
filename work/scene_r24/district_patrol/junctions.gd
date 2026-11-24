extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene);current_scene=scene
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	await frames(30)
	var walker:CharacterBody3D=lesson.demo.walker
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_patrol/measurements.json"))
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.current=true
	RenderingServer.render_loop_enabled=false
	for i in data.landings.size():
		var row:Dictionary=data.landings[i]
		var a:=Vector3(row.entry[0],row.entry[2],-row.entry[1])
		var b:=Vector3(row.exit[0],row.exit[2],-row.exit[1])
		var m:=Vector3(row.center_xy[0],(a.y+b.y)*.5,-row.center_xy[1])
		var direction:=(m-a).normalized()
		a-=direction*1.55;b+=(b-m).normalized()*1.55
		if walker.mounted:
			walker.dismount(a+Vector3.UP*.45,true)
		else:
			walker.global_position=a+Vector3.UP*.45
			walker.velocity=Vector3.ZERO
		var distance_start:float=walker.travelled
		walker.go(PackedVector3Array([m,b,m,a]))
		var completed:=false
		for tick in 1400:
			await physics_frame
			completed=walker.advance(1./60.,true)
			if tick==80 and DisplayServer.get_name()!="headless":
				camera.global_position=walker.global_position-direction*2.6+Vector3.UP*2.1
				camera.look_at(m+Vector3.UP*.45)
				print("LANDING_VIEW ",i," ",camera.global_position," ",m+Vector3.UP*.45," ",camera.fov)
				camera.make_current();camera.force_update_transform()
				await frames(3)
				await capture("landing_%02d"%i)
			if completed:break
		check("mentor_walking_turn_%d"%i,completed and walker.is_on_floor(),{"street":row.street,"distance_m":walker.travelled-distance_start,"end":str(walker.global_position),"waypoints":walker.index})
	check("all_new_landings_tested",data.landings.size()>=3)
	FileAccess.open(output.path_join("turns.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
