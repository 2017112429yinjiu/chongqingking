extends "../../continuous_site_walk.gd"

func point_key(point: Vector3) -> String:
	return "%s,%s,%s" % [roundi(point.x * 1000.), roundi(-point.z * 1000.), roundi(point.y * 1000.)]

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	var reference_path := ""
	for word in OS.get_cmdline_user_args():
		if word.begins_with("--legacy-shell-reference="):
			reference_path = word.trim_prefix("--legacy-shell-reference=")
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(reference_path))
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var matches: Dictionary = {}
	var owner := scene.find_child(reference.owner, true, false) as MeshInstance3D
	assert(owner != null and owner.is_visible_in_tree())
	var faces := owner.mesh.get_faces()
	for first in range(0, faces.size(), 3):
		var triangle := PackedStringArray()
		for corner in range(3):
			triangle.append(point_key(owner.global_transform * faces[first + corner]))
		triangle.sort()
		for pid in reference.triangles.get(";".join(triangle), []):
			matches[pid] = matches.get(pid, 0) + 1
	var named: Dictionary = {}
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for plot: Dictionary in layout.plots:
		var id := "%02d" % plot.plot_id
		var pieces := []
		for prefix in ["COL_Outer500_Frame", "Outer500_Joinery", "Outer500_InteriorFloor", "COL_Outer500_Court", "Outer500_CourtDetails"]:
			var obj := scene.find_child(prefix + "_" + id, true, false) as Node3D
			if obj != null:
				pieces.append({"name": str(obj.name), "visible": obj.is_visible_in_tree()})
		named[str(int(plot.plot_id))] = pieces
	var report := {"matches": matches, "expected": reference.expected, "named": named,
		"base_ownership_plots": reference.ownership_plots, "active_shared_triangle_count": faces.size()/3,
		"runtime": scene.scene_identity.district_500, "engine": Engine.get_version_info().string}
	FileAccess.open(output.path_join("legacy-shells.json"), FileAccess.WRITE).store_string(JSON.stringify(report, "  "))
	check("normal_game_and_legacy_owner", faces.size() > 300 and matches.size() > 0, matches.size())
	quit(2 if ever_failed else 0)
