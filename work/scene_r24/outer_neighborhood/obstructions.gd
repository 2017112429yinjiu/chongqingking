extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in 1600:
		if scene.get("gameplay"):break
		await physics_frame
	await frames(12)
	var report:= []
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for i in data.plots.size():
		var p: Dictionary=data.plots[i]
		var f: float=-p.depth/2
		var u: float=p.door_u
		var cast := []
		for up: float in [.18,.72,1.12,1.62]:
			var a:=world(p,u,f-.91,up)
			var b:=world(p,u,-f+.69,up)
			var ray:=PhysicsRayQueryParameters3D.create(a,b,1)
			ray.hit_back_faces=true
			var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
			if not hit.is_empty():
				cast.append({"h":up,"distance":a.distance_to(hit.position),"mesh":str(hit.collider.get_parent().name),"at":str(hit.position)})
		if not cast.is_empty():report.append({"plot":i,"rays":cast})
	FileAccess.open(output.path_join("obstructions.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	quit()
