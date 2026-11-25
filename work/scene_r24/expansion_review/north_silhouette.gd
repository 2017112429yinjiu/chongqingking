extends SceneTree
## Resolve a registered screenshot pixel against rendered (including non-colliding) geometry.
func _initialize() -> void:
	call_deferred("inspect")

func inspect() -> void:
	var scene: Node3D = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in 1800:
		if scene.get("gameplay"):
			break
		await physics_frame
	if not scene.get("gameplay"):
		quit(2)
		return
	var camera := Camera3D.new()
	camera.fov = 66
	camera.far = 1500
	scene.add_child(camera)
	camera.global_position = Vector3(-30.26,35.09,-93.24)
	camera.look_at(Vector3(-46.3,37.2,-116.17))
	camera.current = true
	await physics_frame
	var mesh_nodes := scene.find_children("*","MeshInstance3D",true,false)
	var records := []
	for pixel: Vector2 in [Vector2(580,153),Vector2(579,148),Vector2(582,158),Vector2(1050,258)]:
		var screen := pixel * camera.get_viewport().get_visible_rect().size / Vector2(1152,648)
		var origin := camera.project_ray_origin(screen)
		var end := origin + camera.project_ray_normal(screen) * 1500.0
		var hits := []
		for item: MeshInstance3D in mesh_nodes:
			if not item.is_visible_in_tree() or not item.mesh:
				continue
			var near_p := item.to_local(origin)
			var far_p := item.to_local(end)
			if item.get_aabb().intersects_segment(near_p, far_p) == null:
				continue
			var direction := (far_p - near_p).normalized()
			var tris := item.mesh.get_faces()
			var nearest := INF
			for i in range(0,tris.size(),3):
				var point: Variant = Geometry3D.ray_intersects_triangle(near_p, direction, tris[i], tris[i+1], tris[i+2])
				if point != null:
					nearest = minf(nearest, origin.distance_to(item.to_global(point)))
			if nearest < 1500.0:
				hits.append([nearest,str(item.get_path()),str(item.global_position)])
		hits.sort_custom(func(a,b):return a[0]<b[0])
		records.append({"pixel":str(pixel),"hits":hits.slice(0,4)})
	var out := OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(out)
	FileAccess.open(out.path_join("pixel_hits.json"),FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	quit()
