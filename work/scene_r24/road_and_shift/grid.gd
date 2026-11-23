extends SceneTree
func _initialize():call_deferred("run")
func run():
	var scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await physics_frame
	var out=FileAccess.open("res://verification_r24/road_shift/grid.json",FileAccess.WRITE)
	var rows=[]
	var space=scene.get_world_3d().direct_space_state
	for z in range(14,62):
		var row=[]
		for x in range(-55,-13):
			var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,23,z),Vector3(x,8,z),1))
			if hit.is_empty():row.append(null)
			else:row.append([snappedf(hit.position.y,.001),str(hit.collider.get_parent().name),snappedf(hit.normal.y,.001)])
		rows.append(row)
	out.store_string(JSON.stringify(rows))
	quit()
