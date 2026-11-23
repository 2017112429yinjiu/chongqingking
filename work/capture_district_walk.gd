extends SceneTree
func _initialize() -> void:
	call_deferred("take")

func take() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null:await physics_frame
	main.hud.visible=false
	var cam:=Camera3D.new()
	main.add_child(cam)
	cam.fov=60
	cam.make_current()
	var count:=241
	var path: Array[Vector3]=[]
	# Sample the actual traversable centre of the stair, then smooth out the
	# step-by-step vertical camera bob as on a stabilised walking shot.
	for i in count:
		var t:=float(i)/(count-1)
		var p:=Vector3(-20.20+.31*sin(PI*t),50,51.2-15.2*t)
		var query:=PhysicsRayQueryParameters3D.create(p,p-Vector3.UP*49,1)
		var hit:=main.get_world_3d().direct_space_state.intersect_ray(query)
		if hit.is_empty():
			push_error("Missing stair contact at "+str(p))
			quit(2)
			return
		path.append(Vector3(p.x,float(hit.position.y)+1.65,p.z))
	for i in range(36+count):
		var k:=clampi(i-36,0,count-1)
		var mean_y:=0.
		for d in range(-7,8):mean_y+=path[clampi(k+d,0,count-1)].y/15.
		cam.global_position=Vector3(path[k].x,mean_y,path[k].z)
		cam.look_at(Vector3(-19.3,23.2,20.0))
		await process_frame
	var directory: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(directory)
	FileAccess.open(directory+"/district_take.json",FileAccess.WRITE).store_string(JSON.stringify({"frames":count,"sample_fps":30,"scene":main.scene_identity.get("district_r21",{}),"profile_sha256":FileAccess.get_sha256(main.art_profile_path),"camera":"continuous terrain-sampled stabilised camera","start":str(path[0]),"end":str(path[-1])},"\t"))
	quit()
