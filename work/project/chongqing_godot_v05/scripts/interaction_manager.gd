extends Node
## World-distance + line-of-sight checks are repeated at execution time.
var targets: Array[Node3D] = []
var actor: Node3D
var current: Node3D

func register(target: Node3D) -> void:
	assert(not target.interaction_id.is_empty())
	for existing in targets:
		assert(existing.interaction_id != target.interaction_id)
	targets.append(target)
	target.tree_exiting.connect(func(): targets.erase(target))

func reachable(target: Node3D) -> bool:
	if not is_instance_valid(target) or not target.available() or not actor.walking:
		return false
	var foot: Vector3 = actor.body.global_position
	if foot.distance_to(target.global_position - Vector3.UP) > target.radius:
		return false
	var query: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(foot + Vector3.UP * 1.3, target.global_position, 1)
	query.exclude = [actor.body.get_rid()]
	return actor.get_world_3d().direct_space_state.intersect_ray(query).is_empty()

func select() -> Node3D:
	current = null
	var best: float = INF
	for target in targets:
		if reachable(target):
			var distance: float = actor.body.global_position.distance_squared_to(target.global_position)
			if distance < best:
				current = target
				best = distance
	return current

func interact() -> bool:
	var selected: Node3D = select()
	if selected == null or not reachable(selected):
		return false
	selected.execute()
	return true
