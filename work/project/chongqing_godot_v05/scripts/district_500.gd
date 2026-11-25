extends RefCounted

const MODEL := "res://assets/district_500/outer_district.glb"
const LAYOUT := "res://assets/district_500/layout.json"

static func install(city: Node3D) -> Dictionary:
	var district := (load(MODEL) as PackedScene).instantiate() as Node3D
	district.name = "OuterDistrict500"
	city.add_child(district)
	var ground := ShaderMaterial.new()
	ground.shader = preload("res://shaders/district_500_ground.gdshader")
	ground.set_shader_parameter("street_mask", load("res://assets/district_500/surface_mask.png"))
	var textures := {
		"asphalt": "asphalt_02_diff_1k.jpg",
		"asphalt_normal": "asphalt_02_nor_gl_1k.jpg",
		"asphalt_rough": "asphalt_02_rough_1k.png",
		"paving": "stone_floor_diff_2k.jpg",
		"soil": "brown_mud_leaves_01_diff_2k.jpg",
		"aggregate": "leaf_scattered_gravel_diff_2k.jpg",
	}
	for key: String in textures:
		ground.set_shader_parameter(key, load("res://assets/chongqing_district_" + textures[key]))
	for tile: MeshInstance3D in district.find_children("COL_Outer500_Surface_*", "MeshInstance3D", true, false):
		tile.material_override = ground
	var local_frame := city.find_child("LocalCityFrame", true, false) as Node3D
	if local_frame:
		local_frame.hide()
	for bank_name in ["R22_Bank_Outer", "R22_Bank_Relief"]:
		var bank := city.find_child(bank_name, true, false) as MeshInstance3D
		if bank:
			(bank.get_surface_override_material(0) as ShaderMaterial).set_shader_parameter("outer_district_cut", true)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	var prefixes: Array = layout.get("retired_context_prefixes", [])
	for prior: MeshInstance3D in city.find_children("Context_*","MeshInstance3D",true,false):
		for prefix: String in prefixes:
			if str(prior.name).begins_with(prefix):
				prior.hide()
				break
	var roofs := city.find_child("R21_Rooftop_stairheads",true,false) as MeshInstance3D
	if roofs and not layout.get("retired_roof_positions",[]).is_empty():
		trim_roofs(roofs,layout.retired_roof_positions)
	var trunks := StaticBody3D.new()
	trunks.name = "OuterDistrictTreeTrunks"
	trunks.collision_layer = 1
	trunks.collision_mask = 0
	district.add_child(trunks)
	# Near trees keep the scanned leaves. Beyond the pavement use the same species'
	# four-direction atlas as the existing hillside, grouped into small street cells.
	var distant_trees := []
	var tree_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/layout.json"))
	for plant: MeshInstance3D in district.find_children("Outer500_Plant_*", "MeshInstance3D", true, false):
		plant.lod_bias = 5.0
		plant.visibility_range_end = 38.0
	for tree: Dictionary in layout.get("planting", []):
		var p: Array = tree.east_north_up
		var cylinder := CylinderShape3D.new()
		cylinder.radius = 0.13 * tree.width_scale
		cylinder.height = 1.8 * tree.height_scale
		var shape := CollisionShape3D.new()
		shape.shape = cylinder
		shape.position = Vector3(p[0], p[2] + cylinder.height / 2.0, -p[1])
		trunks.add_child(shape)
		var scan_height := 4.54 if int(tree.species) == 0 else 5.02
		distant_trees.append({"position":[p[0], p[2], -p[1]], "height":scan_height * float(tree.height_scale),
			"kind":tree.species, "yaw":deg_to_rad(tree.rotation_deg), "shade":0.94})
	preload("res://scripts/district_r21.gd").install_canopy(district, distant_trees, tree_data.canopy_pivots, 8.0, 34.0)
	var retire: Array = layout.get("osm_building_ids", [])
	for id: int in retire:
		for prior: Node3D in city.find_children("Context_*%s_*" % id, "MeshInstance3D", true, false):
			prior.hide()
	for place: Dictionary in layout.destinations:
		var sign := Label3D.new()
		var northeast: Array = place.east_north
		var angle: float = place.bearing
		var offset: float = place.front_offset - 0.27
		sign.position = Vector3(northeast[0] - sin(angle) * offset, place.height + 2.38,
			-northeast[1] - cos(angle) * offset)
		sign.rotation.y = angle
		sign.text = place.name
		sign.modulate = Color("#f0e2b9")
		sign.outline_modulate = Color("#2d2822")
		sign.outline_size = 12
		sign.font = load("res://assets/district_500/district_signs.otf")
		sign.font_size = 72
		sign.pixel_size = 0.0051
		sign.no_depth_test = false
		district.add_child(sign)
	return {"bounds_east_north_m": layout.bounds_east_north_m,
		"glb_sha256": FileAccess.get_sha256(MODEL), "retired_internal_context": local_frame != null, "osm_building_ids": retire}


static func trim_roofs(node: MeshInstance3D, anchors: Array) -> void:
	var original := node.mesh
	var retained := ArrayMesh.new()
	for surface in original.get_surface_count():
		var arrays := original.surface_get_arrays(surface)
		var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		if indices.is_empty():
			indices=PackedInt32Array(range(positions.size()))
		var keep := PackedInt32Array()
		for i in range(0,indices.size(),3):
			var center := node.to_global((positions[indices[i]]+positions[indices[i+1]]+positions[indices[i+2]])/3.0)
			var removed := false
			for a: Array in anchors:
				if absf(center.x-a[0])<2.35 and absf(center.z-a[2])<1.65 and center.y>a[1]-.10 and center.y<a[1]+4.65:
					removed=true
					break
			if not removed:
				keep.append_array(indices.slice(i,i+3))
		if not keep.is_empty():
			arrays[Mesh.ARRAY_INDEX]=keep
			retained.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
			retained.surface_set_material(retained.get_surface_count()-1,node.get_active_material(surface))
	node.mesh=retained

static func start_exploration(scene: Node3D) -> void:
	var collision := preload("res://scripts/build_collisions.gd")
	var bike := scene.gameplay.scooter as CharacterBody3D
	var road := collision.raycast_ground(scene, Vector3(102.0, 21.0, 42.1), 10.0)
	var shoulder := collision.raycast_ground(scene, Vector3(101.1, 21.0, 41.1), 10.0)
	if road.is_empty() or shoulder.is_empty():
		push_error("The 500 m exploration entry lost its road support")
		return
	bike.global_position = road.position + Vector3.UP * 0.035
	bike.safe_park_position = bike.global_position
	bike.rotation.y = -0.87
	scene.explorer.set_walk_origin(shoulder.position + Vector3.UP * 0.035, bike.global_position + Vector3.UP)
