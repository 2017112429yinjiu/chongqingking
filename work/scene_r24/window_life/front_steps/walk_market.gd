extends SceneTree

func _initialize() -> void:
	call_deferred("walk")

func walk() -> void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var walker=game.explorer
	var folder: String=OS.get_cmdline_user_args()[-1]
	DirAccess.make_dir_recursive_absolute(folder)
	game.hud.hide()
	var waypoints: Array[Vector3]=[Vector3(-21.48,7.84,80.59),Vector3(-21.48,8.85,76.62),Vector3(-25.3,8.88,76.22)]
	var start:=Vector3(-24.4,8.0,81.17)
	var hit: Dictionary=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP, start-Vector3.UP,1))
	if hit.is_empty():quit(2);return
	walker.begin_route_test(hit.position+Vector3.UP*.035,waypoints[0])
	for i in 10:await physics_frame
	var previous: Vector3=walker.body.global_position
	var total:=0.0
	var max_step:=0.0
	var timeline: Array=[]
	var goals: Array=[]
	var frame:=0
	var nearby: Dictionary={}
	var probes: Array=[]
	for t in game.street_block.tracks:
		if not t.car:probes.append([t.node,"%s:%s" % [t.route,t.node.name]])
	for sk in game.get_node("City").find_children("*","Skeleton3D",true,false):
		if sk.get_parent() is Node3D:
			probes.append([sk, str(sk.get_path())])

	var focus:=Vector3(-21.45,8.54,78.45)
	for stage in waypoints.size():
		var goal:=waypoints[stage]
		var reached:=false
		for tick in 400:
			var position: Vector3=walker.body.global_position
			var target:=Vector3(-21.25,8.50,78.55)
			if stage>=1:
				var blend:=smoothstep(80.0,76.75,position.z)
				target=target.lerp(Vector3(-27.0,10.05,73.55),blend)
			focus=focus.lerp(target,.055)
			walker.camera.look_at(focus,Vector3.UP)
			walker._sync_angles()
			var forward: Vector3=-walker.camera.global_basis.z
			forward.y=0.0
			forward=forward.normalized()
			var direction:=goal-position
			direction.y=0.0
			if direction.length()<.20:
				reached=true
				break
			direction=direction.normalized()
			walker.automation_axis=Vector2(direction.dot(forward.cross(Vector3.UP)),-direction.dot(forward))*.71
			await physics_frame
			var current: Vector3=walker.body.global_position
			for probe in probes:
				var at: Vector3=probe[0].global_position
				if absf(at.y-current.y)>1.4:continue
				var distance := Vector2(current.x-at.x,current.z-at.z).length()
				if distance<1.65 and (not nearby.has(probe[1]) or distance<nearby[probe[1]].gap):
					nearby[probe[1]]={"gap":distance,"tick":frame,"where":[at.x,at.y,at.z],"foot":[current.x,current.y,current.z]}
			max_step=maxf(max_step,previous.distance_to(current))
			total+=Vector2(current.x-previous.x,current.z-previous.z).length()
			previous=current
			if frame%6==0:
				await RenderingServer.frame_post_draw
				var img:=root.get_texture().get_image()
				if img.is_empty() or img.save_jpg(folder.path_join("frame_%03d.jpg"%timeline.size()),.92)!=OK:quit(3);return
				timeline.append({"tick":frame,"stage":stage,"foot":[current.x,current.y,current.z]})
			frame+=1
		goals.append(reached)
		if not reached:break
	walker.end_route_test()
	var report={"passed":goals.size()==3 and not goals.has(false) and max_step<.28,
		"goals":goals,"closest":nearby,"path":timeline,"metres":total,"max_step_m":max_step}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	FileAccess.open(folder+"/walk.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("MARKET16_APPROACH ",report.passed," ",goals," ",total," ",max_step," ",timeline.size())
	quit(0 if report.passed else 5)
