extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(10)
	var space:=scene.get_world_3d().direct_space_state;var rows:=[]
	for pt:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/slope_grid_gaps.json")):
		var p:=Vector3(pt[0],70.,pt[1]);var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p,p-Vector3.UP*90.,1))
		rows.append([pt,null if hit.is_empty() else hit.position.y,"" if hit.is_empty() else str(hit.collider.get_parent().name)])
	FileAccess.open(output.path_join("margins.json"),FileAccess.WRITE).store_string(JSON.stringify(rows))
	quit()
