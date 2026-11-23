extends SceneTree

func _initialize() -> void:
	call_deferred("record_take")

func record_take() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	await physics_frame
	main.hud.visible=false
	var camera:=Camera3D.new()
	main.add_child(camera)
	camera.fov=56
	camera.far=main.explorer.camera.far
	camera.make_current()
	var space:=main.get_world_3d().direct_space_state
	var count:=241
	var path:Array[Vector3]=[]
	var touched:Dictionary={}
	var max_step:=0.
	for i in count:
		var t:=float(i)/(count-1)
		var z:=56.2+9.8*smoothstep(.42,1.,t)
		var probe:=Vector3(lerpf(-27.,-45.,t),15.,z)
		var floor_hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(probe,probe-Vector3.UP*8.,1))
		if floor_hit.is_empty():
			push_error("Ground missing at "+str(probe))
			quit(2)
			return
		var pos:Vector3=floor_hit.position+Vector3.UP*1.65
		var body_name:=str(floor_hit.collider.get_parent().name)+"/"+str(floor_hit.collider.name)
		touched[body_name]=int(touched.get(body_name,0))+1
		if not path.is_empty():
			max_step=maxf(max_step,absf(pos.y-path[-1].y))
			var crossing:=space.intersect_ray(PhysicsRayQueryParameters3D.create(path[-1],pos,1))
			if not crossing.is_empty() or max_step>.28:
				push_error("Discontinuous street take at "+str(probe)+" on "+body_name+" step "+str(max_step))
				quit(2)
				return
		path.append(pos)
	var first:=(Vector3(-30.48,12.23,61.)-path[0]).normalized()
	var last:=(Vector3(-502,30,578)-path[-1]).normalized()
	for i in range(36+count):
		var k:=clampi(i-36,0,count-1)
		var fraction:=smoothstep(.08,.88,float(k)/(count-1))
		var height:=0.
		for j in range(-4,5):height+=path[clampi(k+j,0,count-1)].y/9.
		camera.global_position=Vector3(path[k].x,height,path[k].z)
		camera.look_at(camera.global_position+first.slerp(last,fraction))
		await process_frame
	var dir:String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(dir)
	var data:Dictionary={"frames":count,"sample_fps":30,"start":str(path[0]),"end":str(path[-1]),
		"support_samples":touched,"largest_floor_step_m":max_step,"eye_m":1.65,
		"camera":"continuous collision-sampled walking shot","art_revision":main.scene_identity,
		"profile_sha256":FileAccess.get_sha256(main.art_profile_path)}
	FileAccess.open(dir+"/district_take.json",FileAccess.WRITE).store_string(JSON.stringify(data,"\t"))
	quit()
