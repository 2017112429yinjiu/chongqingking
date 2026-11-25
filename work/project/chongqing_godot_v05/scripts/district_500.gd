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
	var retire: Array = layout.get("osm_building_ids", [])
	for id: int in retire:
		for prior: Node3D in city.find_children("Context_*%s_*" % id, "MeshInstance3D", true, false):
			prior.hide()
	for place: Dictionary in layout.destinations:
		var sign := Label3D.new()
		var northeast: Array = place.east_north
		var angle: float = place.bearing
		var offset: float = place.front_offset - 0.14
		sign.position = Vector3(northeast[0] - sin(angle) * offset, place.height + 2.47,
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
	bike.rotation.y = -2.21
	scene.explorer.set_walk_origin(shoulder.position + Vector3.UP * 0.035, bike.global_position + Vector3.UP)
