extends SceneTree

func _initialize() -> void:call_deferred("survey")

func survey() -> void:
	var world:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(world)
	while world.street_block==null or world.street_block.tracks.size()!=8:await physics_frame
	var block: Node3D=world.street_block
	var directory:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/traffic")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var out: Array=[]
	for t in block.tracks:
		if not t.car or str(t.node.name).contains("@"):continue
		var curve: Curve3D=block.routes[t.route]
		var samples: Array=[]
		for i in range(0,int(curve.get_baked_length()),3):
			t.d=float(i)
			block._pose(t,0.,true)
			for h in t.hubs:
				var p: Vector3=h.global_position
				var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.70,p-Vector3.UP*9.,1)
				var hit:=world.get_world_3d().direct_space_state.intersect_ray(q)
				var origin: Vector3=h.position
				if not hit.is_empty():
					samples.append([i,p.x,p.z,p.y-origin.y-hit.position.y,str(hit.collider.get_parent().name)])
				else:samples.append([i,p.x,p.z,null,""])
		out.append({"route":t.route,"car":str(t.node.name),"samples":samples})
	var report:={"tracks":out}
	preload("res://scripts/qa_context.gd").decorate(report,world)
	FileAccess.open(directory+"/traffic.json",FileAccess.WRITE).store_string(JSON.stringify(report," "))
	print("TRAFFIC SURVEY ",out.size())
	quit()

