class_name CQDistrictCollisions
extends RefCounted
## Selective world collision for the imported Chongqing block.
## GLB is already metre-scaled and Y-up. Shapes inherit each mesh's local
## transform, which also preserves the rotated, batched original stair mesh.

const WORLD_LAYER: int = 1
const BODY_NAME: StringName = &"CQ_StaticCollision"


static func attach(root: Node3D) -> Dictionary:
	var result: Dictionary = {
		"bodies": 0,
		"created": 0,
		"reused": 0,
		"triangles": 0,
		"skipped_meshes": 0,
		"by_kind": {},
		"failed": [],
	}
	var meshes: Array[MeshInstance3D] = []
	_collect_meshes(root, meshes)
	for instance: MeshInstance3D in meshes:
		var kind: String = _collision_kind(String(instance.name))
		if String(instance.name).begins_with("COLH_"):
			instance.visible = false
		if kind.is_empty() or instance.mesh == null:
			result["skipped_meshes"] += 1
			continue
		var existing: StaticBody3D = instance.get_node_or_null(NodePath(BODY_NAME)) as StaticBody3D
		if existing != null:
			result["reused"] += 1
			result["bodies"] += 1
			result["triangles"] += int(existing.get_meta("cq_triangle_count", 0))
			_count_kind(result, kind)
			continue
		# Use Godot's imported face winding, rather than reconstructing Blender
		# coordinates. Detailed windows, railings, leaves and props stay visual.
		var shape: ConcavePolygonShape3D = instance.mesh.create_trimesh_shape()
		if shape == null:
			result["failed"].append(String(instance.name))
			continue
		# Road ribbons and the hillside include open surfaces. Two-sided static
		# contact keeps them robust when approached from their exposed edges.
		shape.backface_collision = true
		var body := StaticBody3D.new()
		body.name = BODY_NAME
		body.collision_layer = WORLD_LAYER
		body.collision_mask = 0
		body.set_meta("cq_collision_kind", kind)
		var triangle_count: int = shape.get_faces().size() / 3
		body.set_meta("cq_triangle_count", triangle_count)
		instance.add_child(body)
		var collision := CollisionShape3D.new()
		collision.name = &"Surface"
		collision.shape = shape
		body.add_child(collision)
		result["bodies"] += 1
		result["created"] += 1
		result["triangles"] += triangle_count
		_count_kind(result, kind)
	return result


static func _count_kind(result: Dictionary, kind: String) -> void:
	var kinds: Dictionary = result["by_kind"]
	kinds[kind] = int(kinds.get(kind, 0)) + 1


static func _collect_meshes(node: Node, result: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		result.append(node as MeshInstance3D)
	for child: Node in node.get_children():
		if not child is CollisionObject3D:
			_collect_meshes(child, result)


static func _collision_kind(mesh_name: String) -> String:
	if mesh_name.begins_with("COL_") or mesh_name.begins_with("COLH_"):
		return "refined_structure"
	if mesh_name == "Designed_Hillside_200m":
		return "terrain"
	if mesh_name.begins_with("OSM_Building_"):
		return "building"
	if mesh_name.begins_with("Foundation_"):
		return "foundation"
	if mesh_name.begins_with("OSM_Road_"):
		return "road"
	if mesh_name.begins_with("WalkwayDetails_CQ_paving") or mesh_name.begins_with("OSM_Path_") or mesh_name.begins_with("OSM_Underground_Footpath_"):
		return "walkway"
	if mesh_name.begins_with("Bridge_Deck"):
		return "bridge"
	if mesh_name.begins_with("RoadMarkings_CQ_paving"):
		return "curb"
	# Roof_Access and Roof_Tank are decorative: only the numbered roof cap
	# supplies the visible rooftop surface over the main building body.
	if mesh_name.begins_with("Roof_") and mesh_name.trim_prefix("Roof_").get_slice(".", 0).is_valid_int():
		return "roof"
	return ""


## Call after at least one physics frame with the scene inside the tree.
## `from` must be above the desired surface, below higher roofs when a street
## is intended. Returns the normal PhysicsDirectSpaceState3D ray dictionary.
static func raycast_ground(world_node: Node3D, from: Vector3, distance: float = 100.0, exclude: Array[RID] = []) -> Dictionary:
	if not world_node.is_inside_tree():
		return {}
	var query := PhysicsRayQueryParameters3D.create(from, from + Vector3.DOWN * distance, WORLD_LAYER, exclude)
	query.collide_with_areas = false
	query.hit_back_faces = true
	return world_node.get_world_3d().direct_space_state.intersect_ray(query)
