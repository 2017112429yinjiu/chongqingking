extends "../../../day_one/verify.gd"

const Collision := preload("res://scripts/build_collisions.gd")
const District := preload("res://scripts/district_500.gd")
const PLOTS := ["00", "01", "12", "22", "26", "30", "31", "34", "35", "40",
	"41", "42", "43", "45", "46", "49", "52", "53", "54", "56"]
const SHORTCUTS := ["00-tool-eye", "34-street"]

func enu(value: Vector3) -> Array:
	return [value.x, -value.z, value.y]

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var district: Node3D = scene.get_node("City/OuterDistrict500")
	var anchors: Dictionary = district.get_meta("acceptance_player_points")
	var entries: Dictionary = {}
	for id: String in PLOTS + SHORTCUTS:
		var spec: Array = anchors.get(id, [])
		var hit: Dictionary = {}
		if spec.size() == 2:
			hit = Collision.raycast_ground(scene, District.enu(spec[0]) + Vector3.UP * .30, .95)
		check("registered_ground_" + id, not hit.is_empty())
		entries[id] = {"editor_enu_m": spec[0] if spec.size() == 2 else [],
			"look_enu_m": spec[1] if spec.size() == 2 else [],
			"supported_enu_m": enu(hit.position) if hit else [],
			"support": str(hit.collider.get_parent().name) if hit else ""}
	var player: CharacterBody3D = scene.explorer.body
	var expected := District.enu(anchors["43"][0])
	check("normal_exploration_starts_at_plot43", player.global_position.distance_to(expected) < .40,
		enu(player.global_position))
	FileAccess.open(output.path_join("plot-entries.json"), FileAccess.WRITE).store_string(
		JSON.stringify({"plots": PLOTS, "shortcuts": SHORTCUTS, "entries": entries, "checks": checks}, "  "))
	quit(2 if ever_failed else 0)
