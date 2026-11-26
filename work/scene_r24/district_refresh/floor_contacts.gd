extends "../outer_neighborhood/survey.gd"


func terrain_under(point: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(point + Vector3.UP * 2.3, point - Vector3.UP * 4, 1)
	var excluded: Array[RID] = []
	for i in range(20):
		query.exclude = excluded
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
		if hit.is_empty():
			return {}
		var parent: Node = hit.collider.get_parent()
		if str(parent.name).begins_with("COL_Outer500_Surface_"):
			return {"mesh": str(parent.name), "height_m": hit.position.y, "rise_m": hit.position.y - point.y}
		excluded.append(hit.rid)
	return {}

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	var registered_path := OS.get_environment("CQ_REGISTERED_PROBES")
	var registered: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(registered_path))
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in range(1600):
		if scene.gameplay:
			break
		await physics_frame
	if not check("gameplay_loaded", scene.gameplay != null):
		quit(2)
		return
	await frames(25)
	for place: String in registered.intrusions:
		var q: Array = registered.intrusions[place].xy
		var result := terrain_under(Vector3(q[0], q[2], -q[1]))
		check(place, not result.is_empty() and result.get("rise_m", INF) < -.02, result)
	FileAccess.open(output.path_join("contacts.json"), FileAccess.WRITE).store_string(JSON.stringify(checks, "  "))
	quit(2 if ever_failed else 0)
