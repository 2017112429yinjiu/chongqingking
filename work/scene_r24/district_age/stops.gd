extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(10)
	var space:=scene.get_world_3d().direct_space_state;var out:={}
	for v:Array in [[23,Vector3(50.01,11.82,62.06),Vector3(51.56,12.208,61.719)],[24,Vector3(-21.1,31.88,-80.59),Vector3(-20.78,32.50,-81.92)],[25,Vector3(-73.81,31.0,-84.82),Vector3(-75.036,31.06,-85.55)],[27,Vector3(61.69,30.436,-56),Vector3(63,30.83,-56)]]:
		var start:Vector3=v[1];var dir:Vector3=v[2]-start;dir.y=0;dir=dir.normalized()
		var hits:=[]
		for k in [0.06,.11,.17,.25,.33,.46,.60,.85,1.1,1.45]:
			for e in [-.3,0.,.3]:
				var p:Vector3=start+Vector3.UP*k+dir.cross(Vector3.UP)*e
				var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p,p+dir*2.7,1))
				if h:hits.append([k,e,str(h.collider.get_parent().name),str(h.position)])
		out[str(v[0])]=hits
	FileAccess.open(output.path_join("contacts.json"),FileAccess.WRITE).store_string(JSON.stringify(out))
	quit()
