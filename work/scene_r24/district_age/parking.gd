extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	var report:={}
	var space:=scene.get_world_3d().direct_space_state
	var exclude:Array[RID]=[]
	for body in scene.find_children("ParkedCar*","StaticBody3D",true,false):exclude.append(body.get_rid())
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/frontage_r24/frontage.json"))
	for key:String in plan.parked_contacts:
		var wheels:=[]
		for m:MeshInstance3D in scene.find_children(key+"*","MeshInstance3D",true,false):
			if not m.is_visible_in_tree() or not m.mesh:continue
			var samples:=[]
			for idx in m.mesh.get_surface_count():
				var vs:PackedVector3Array=m.mesh.surface_get_arrays(idx)[Mesh.ARRAY_VERTEX]
				for v in vs:samples.append(m.global_transform*v)
			var err:=[]
			for q:Array in plan.parked_contacts[key]:
				var lowest:=INF
				for p:Vector3 in samples:
					if Vector2(p.x-q[0],p.z-q[2]).length()>.28 or p.y>q[1]+.15:continue
					var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.13,p-Vector3.UP*.8,1)
					ray.exclude=exclude
					var hit:=space.intersect_ray(ray)
					if hit:lowest=minf(lowest,p.y-hit.position.y)
				if lowest<INF:err.append(lowest)
			wheels.append([str(m.name),err])
		report[key]=wheels
	FileAccess.open(output.path_join("tyres.json"),FileAccess.WRITE).store_string(JSON.stringify(report))
	quit()
