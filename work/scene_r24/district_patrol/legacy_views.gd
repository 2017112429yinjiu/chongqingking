extends "../../scene_r24/day_one/verify.gd"

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(30)
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	var walker:CharacterBody3D=lesson.demo.walker
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	RenderingServer.render_loop_enabled=false
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.current=true
	camera.fov=64.
	var points:Array=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_patrol/legacy_turns.json"))
	for i in points.size():
		var c:Array=points[i].centre
		var target:=Vector3(c[0],c[2],-c[1])
		if points[i].has("approach"):
			var way:=PackedVector3Array()
			for p:Array in [points[i].approach[0],c,points[i].approach[1]]:
				var ground:=Vector3(p[0],p[2]+1.4,-p[1])
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(ground,ground-Vector3.UP*3.,1))
				if hit.is_empty():break
				way.append(hit.position)
			if check("crossing_surfaces_%d"%i,way.size()==3):
				if walker.mounted:walker.dismount(way[0]+Vector3.UP*.20,true)
				else:walker.global_position=way[0]+Vector3.UP*.20
				walker.velocity=Vector3.ZERO
				walker.go(PackedVector3Array([way[1],way[2],way[1],way[0]]))
				var done:=false
				for t in 1600:
					await physics_frame
					done=walker.advance(1./60.,true)
					if done:break
				check("old_street_crossing_%d"%i,done and walker.is_on_floor(),{"goals":walker.index,"end":str(walker.global_position)})
		else:check("crossing_endpoints_%d"%i,false)
		for side in 4:
			var angle:float=PI*(.25+.5*side)
			camera.global_position=target+Vector3(cos(angle)*4.3,2.75,sin(angle)*4.3)
			camera.look_at(target+Vector3.UP*.34)
			await frames(5)
			await capture("turn_%02d_%d"%[i+1,side])
	FileAccess.open(output.path_join("crossings.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
