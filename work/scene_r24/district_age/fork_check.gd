extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(6)
	var space:=scene.get_world_3d().direct_space_state
	var rows:=[]
	for x:float in [43.,45.2,46.55,46.98,47.005,47.05,47.18,47.65,48.5,50.]:
		var heights:=[]
		for j in range(53):
			var z:=68.+j*.2
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,13,z),Vector3(x,6,z),1)
			var hit:=space.intersect_ray(ray)
			heights.append(null if hit.is_empty() else [snappedf(hit.position.y,.001),str(hit.collider.get_parent().name)])
		rows.append([x,heights])
	FileAccess.open(output.path_join("fork.json"),FileAccess.WRITE).store_string(JSON.stringify(rows))
	quit()
