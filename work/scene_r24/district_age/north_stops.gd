extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(10)
	var space:=scene.get_world_3d().direct_space_state;var out:={}
	for v:Array in [[4,Vector3(66.85,33.624,-72.98),Vector3(66.81,33.74,-75.62)],[40,Vector3(66.8,33.74,-75.52),Vector3(66.83,33.66,-73.82)],[5,Vector3(64.8576,33.723,-77.207),Vector3(63.652,33.695,-77.438)]]:
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
