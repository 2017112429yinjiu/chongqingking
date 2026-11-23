extends SceneTree

func _initialize() -> void:
	call_deferred("sample")

func sample() -> void:
	var scene = load("res://main.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay: await physics_frame
	await physics_frame
	var space = scene.get_world_3d().direct_space_state
	var shape := CapsuleShape3D.new()
	shape.height = 1.8
	shape.radius = .55
	for z in range(18,77,2):
		var row := ""
		for x in range(-32,15,2):
			var start := Vector3(x,22,z)
			var hit = space.intersect_ray(PhysicsRayQueryParameters3D.create(start,Vector3(x,4,z),1))
			if hit.is_empty() or hit.position.y > 19 or hit.normal.y < .9:
				row += "  # "
				continue
			var qry := PhysicsShapeQueryParameters3D.new()
			qry.shape = shape
			qry.collision_mask = 1
			qry.transform.origin = hit.position + Vector3.UP * 1.03
			row += "%3d " % roundi(hit.position.y*10) if space.intersect_shape(qry,1).is_empty() else "  X "
		print("LAND ",z," ",row)
	quit()
