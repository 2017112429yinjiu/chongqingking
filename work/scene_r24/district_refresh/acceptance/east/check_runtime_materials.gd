extends "../../continuous_site_walk.gd"

const MATERIAL_PLAN := "res://assets/district_500/acceptance-east.json"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var layer: Node = scene.get_node("City/OuterDistrict500/Acceptance_east")
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATERIAL_PLAN))
	var rows := []
	var roots := []
	var categories := {}
	var floor_y := 38.124656545924175 + .893
	for geom: MeshInstance3D in layer.find_children("*", "MeshInstance3D", true, false):
		if not String(geom.name).begins_with("Review01") and not String(geom.name).begins_with("Review22"):
			continue
		var lowest := INF
		for slot in geom.mesh.get_surface_count():
			var material := geom.mesh.surface_get_material(slot) as StandardMaterial3D
			if not material or not plan.pbr_maps.has(material.resource_name):
				continue
			var arrays := geom.mesh.surface_get_arrays(slot)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV] if arrays[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
			var valid_texture_paths := (
				material.albedo_texture != null and material.normal_texture != null
				and material.normal_enabled and material.roughness_texture != null
			)
			var name := material.resource_name
			var material_files: Array = plan.pbr_maps[name]
			var packed: bool = material_files.size() > 2 and material_files[2]
			var channel := BaseMaterial3D.TEXTURE_CHANNEL_GREEN if packed else BaseMaterial3D.TEXTURE_CHANNEL_RED
			var shapes := uv_areas(uv, arrays[Mesh.ARRAY_INDEX])
			var passed := valid_texture_paths and uv.size() == verts.size() and shapes > 0
			var paths := []
			if valid_texture_paths:
				paths = [material.albedo_texture.resource_path, material.normal_texture.resource_path, material.roughness_texture.resource_path]
				passed = passed and paths == [plan.surface_textures[name], material_files[0], material_files[1]]
				passed = passed and material.roughness_texture_channel == channel
				if material_files.size() > 4:
					passed = passed and is_equal_approx(material.normal_scale, float(material_files[3]))
					passed = passed and is_equal_approx(material.metallic_specular, float(material_files[4]))
			check(str(geom.name) + ":" + name, passed)
			rows.append({"mesh":str(geom.name),"material":name,"textures":paths,"uv_vertices":uv.size(),
				"geometry_vertices":verts.size(),"nondegenerate_uv_triangles":shapes,
				"roughness_channel":material.roughness_texture_channel,"normal_strength":material.normal_scale,
				"metallic_specular":material.metallic_specular})
			categories[name] = true
			for v: Vector3 in verts:
				lowest = minf(lowest, (geom.global_transform * v).y)
		if String(geom.name).begins_with("Review01_Ginger_"):
			var gap := lowest - floor_y
			check(str(geom.name) + "_liner_contact", absf(gap - .002) < .0025, gap)
			roots.append({"mesh":str(geom.name),"lowest_y":lowest,"paper_liner_y":floor_y,"gap_m":gap})
	check("seven_scan_instances", roots.size() == 7, roots.size())
	for group: Dictionary in [
		{"match":"skin ", "count":16}, {"match":"vegetable leaf tone ","count":4},
		{"match":"washed sandstone panel ","count":5}, {"match":"dense mown turf","count":1},
		{"match":"light gravel ","count":4}, {"match":"purple shrub leaf ","count":3},
		{"match":"radial planting leaf ","count":3}
	]:
		var names := []
		for label: String in categories:
			if label.contains(group.match):
				names.append(label)
		check("coverage_" + group.match, names.size() >= int(group.count), names)
	FileAccess.open(output.path_join("east-native-materials.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"engine":Engine.get_version_info().string,
		"east_glb_sha256":FileAccess.get_sha256("res://assets/district_500/acceptance-east.glb"),
		"checks":checks,"sampled_surfaces":rows,"ginger_tray_contacts":roots
	}, "  "))
	quit(2 if ever_failed else 0)

func uv_areas(uv: PackedVector2Array, indices: Variant) -> int:
	if uv.is_empty():
		return 0
	var indexed: bool = indices != null and indices.size() > 0
	var count: int = indices.size() if indexed else uv.size()
	var shapes := 0
	for i in range(0,count - 2,3):
		var a := uv[indices[i] if indexed else i]
		var b := uv[indices[i+1] if indexed else i+1]
		var c := uv[indices[i+2] if indexed else i+2]
		if absf((b-a).cross(c-a)) > .000000001:
			shapes += 1
	return shapes
