extends RefCounted
## Simple stable trunk/post volumes. Leaves, wires and lamp heads stay visual.
static func attach(city: Node3D) -> Dictionary:
	var unique: Dictionary = {}
	var count: int = 0
	for mesh: Node in city.find_children("*", "MeshInstance3D", true, false):
		var key: String = ""
		var radius: float = 0.0
		var height: float = 0.0
		if str(mesh.name).begins_with("Planted_tree_"):
			key = str(mesh.name).get_slice("_",2)
			key = "tree_" + key
			radius = .48
			height = 2.3
		elif str(mesh.name).begins_with("CQF_StreetLamp_black_metal"):
			key = str(mesh.name)
			radius = .065
			height = 3.1
		if key.is_empty() or unique.has(key):
			continue
		unique[key] = true
		var body: StaticBody3D = StaticBody3D.new()
		body.name = "PropObstacle_" + key
		body.collision_layer = 1
		body.collision_mask = 0
		city.add_child(body)
		body.global_position = mesh.global_position
		var shape: CylinderShape3D = CylinderShape3D.new()
		shape.radius = radius
		shape.height = height
		var collider: CollisionShape3D = CollisionShape3D.new()
		collider.shape = shape
		collider.position.y = height*.5
		body.add_child(collider)
		count += 1
	return {"trunks_and_posts":count,"method":"deduplicated root-aligned cylinders; foliage excluded"}
