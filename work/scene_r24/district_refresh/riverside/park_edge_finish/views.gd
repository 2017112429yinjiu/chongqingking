extends "../park_plot59/walk.gd"

const FINISH := "res://assets/district_500/park-edge-finish.json"

func site_plan() -> Dictionary:
	var route := super.site_plan()
	var finish: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FINISH))
	var bare := "--qa-without-park-edge-finish" in OS.get_cmdline_user_args()
	var trees := []
	for spec: Dictionary in finish.planted_trees:
		var tree := scene.find_child(spec.name,true,false) as MeshInstance3D
		var original := scene.find_child(spec.donor,true,false) as MeshInstance3D
		trees.append({"name":spec.name,"present":tree!=null,"shared_mesh":
			tree!=null and original!=null and tree.mesh==original.mesh})
	check("tree_band_reuses_licensed_meshes",trees.all(func(row: Dictionary) -> bool:
		return (not row.present) if bare else row.present and row.shared_mesh),trees)
	return route

func eye_frame(label: String, focus: Variant) -> void:
	if label == "street":
		await fixed_view("street-to-59",[-77.45,-181.10,2.22],[-71.75,-191.86,1.19],67.)
		await fixed_view("west-fold-joint",[-78.24,-181.75,1.92],[-76.78,-185.08,.45],53.)
		await fixed_view("sand-grass-and-tree-plaza",[-73.25,-198.43,2.32],[-66.77,-188.50,.99],66.)
		# The eye is the actual end of the tested Plot 61 walk, with the lens aimed toward the same street.
		await fixed_view("61-eye-back-toward-street",[-45.21526,-203.65730,2.61476],[-52.45,-185.10,2.62],69.)
	elif label == "inside_look_back":
		await super.eye_frame(label,focus)
