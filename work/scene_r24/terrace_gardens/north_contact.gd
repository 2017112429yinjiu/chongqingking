extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	var space:=scene.get_world_3d().direct_space_state
	var rows:=[]
	for q:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/terrace_gardens/north_controls.json")):
		var p:=Vector3(q[2],q[5],q[3])
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.16,p-Vector3.UP*.25,1))
		rows.append(q+[hit.position.y,str(hit.collider.get_parent().name)] if hit else q+[null,""])
	FileAccess.open(output.path_join("north.json"),FileAccess.WRITE).store_string(JSON.stringify(rows))
	quit()
