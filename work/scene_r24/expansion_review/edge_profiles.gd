extends "../../scene_r24/day_one/verify.gd"
## Capture old terrain, road deck and competing colliders separately at the four edges.
func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	for i in 1800:
		if scene.get("gameplay") != null:
			break
		await physics_frame
	if not check("first_shift_loaded", scene.get("gameplay") != null):
		quit(2)
		return
	await frames(8)
	var space := scene.get_world_3d().direct_space_state
	var data := []
	for direction: String in ["west","east","north","south"]:
		for i in range(-100,101,2):
			for radius: float in [99.65,100.35,108.0,150.0,200.0,245.0]:
				var x := float(i) if direction in ["north","south"] else radius * (-1 if direction == "west" else 1)
				var z := float(i) if direction in ["west","east"] else radius * (-1 if direction == "north" else 1)
				data.append([direction,i,radius,x,z,surfaces_at(space, x, z)])
	var grid := []
	for xi in range(-250,251,10):
		for zi in range(-250,251,10):
			# Offset outside cell centres inward to avoid a ray exactly on a perimeter triangle edge.
			var x := clampf(float(xi),-249.9,249.9)
			var z := clampf(float(zi),-249.9,249.9)
			grid.append([x,z,surfaces_at(space, x, z)])
	FileAccess.open(output.path_join("grid_500.json"),FileAccess.WRITE).store_string(JSON.stringify({"spacing_m":10,"boundary_inset_m":0.1,"samples":grid}))
	var record := {"entry":"res://first_shift.tscn","fields":["edge","along","radius","x","z","surfaces [parent, body, height, normal.y]"],"samples":data}
	FileAccess.open(output.path_join("edge_profile.json"),FileAccess.WRITE).store_string(JSON.stringify(record))
	quit(0)

func surfaces_at(space: PhysicsDirectSpaceState3D, x: float, z: float) -> Array:
	var query := PhysicsRayQueryParameters3D.create(Vector3(x,130,z), Vector3(x,-35,z),1)
	var surfaces := []
	var excluded: Array[RID] = []
	for step in 16:
		var hit := space.intersect_ray(query)
		if hit.is_empty():
			break
		var body := hit.collider as Node3D
		surfaces.append([str(body.get_parent().name),str(body.name),snappedf(hit.position.y,.001),snappedf(hit.normal.y,.001)])
		excluded.append(hit.rid)
		query.exclude = excluded
	return surfaces
