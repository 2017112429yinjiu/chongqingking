extends RefCounted

const USE_MAP = preload("res://assets/street_use_r24/street_use.png")
const DRESSED = preload("res://shaders/dressed_stone_r24.gdshader")
const PROPS = "res://assets/street_use_r24/workday.glb"

static func install(city: Node3D) -> Dictionary:
	var stats := {"dressed":0, "paving":0, "facades":0, "asphalt":0, "workday":false}
	var stone := ShaderMaterial.new()
	stone.shader = DRESSED
	stone.set_shader_parameter("street_history", USE_MAP)
	stone.set_shader_parameter("stone_scan", preload("res://assets/district_r21/terraces_washed_sandstone.jpg"))
	stone.set_shader_parameter("irregular_normal", preload("res://assets/district_r21/terraces_sandstone_cracks_nor_gl_2k.jpg"))
	stone.set_shader_parameter("stone_rough", preload("res://assets/district_r21/terraces_sandstone_cracks_rough_2k.png"))
	var asphalt := ShaderMaterial.new()
	asphalt.shader = preload("res://shaders/asphalt_use_r24.gdshader")
	asphalt.set_shader_parameter("street_history", USE_MAP)
	asphalt.set_shader_parameter("tar_scan",preload("res://assets/chongqing_district_asphalt_02_diff_1k.jpg"))
	asphalt.set_shader_parameter("tar_normal",preload("res://assets/chongqing_district_asphalt_02_nor_gl_1k.jpg"))
	asphalt.set_shader_parameter("tar_rough",preload("res://assets/chongqing_district_asphalt_02_rough_1k.png"))
	var treated := {}
	for node in city.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if not mi.mesh or not mi.is_visible_in_tree():
			continue
		if str(mi.name).begins_with("R21_Dressed_"):
			mi.material_override = stone
			stats.dressed += 1
			continue
		if not str(mi.name).begins_with("COL_"):
			continue
		if str(mi.name).begins_with("COL_Road_") and str(mi.name).ends_with("_asphalt"):
			mi.material_override = asphalt
			stats.asphalt += 1
			continue
		for surface in mi.mesh.get_surface_count():
			var mat := mi.get_active_material(surface) as ShaderMaterial
			if not mat or not mat.shader:
				continue
			var shader_path := mat.shader.resource_path
			var wall := false
			var paving := shader_path.ends_with("/paving_r21.gdshader") or str(mi.name) in ["COL_R23_NanquSidewalk","COL_R23_NanquUpperApron"]
			if shader_path.ends_with("/street_surface_r19.gdshader"):
				paving = float(mat.get_shader_parameter("surface_kind")) < .5
				wall = not paving and str(mi.name).begins_with("COL_B_")
			if shader_path.ends_with("/frontage_surface_r24.gdshader"):
				paving = str(mi.name).begins_with("COL_R24_MarketStairs")
			if not paving and not wall:
				continue
			var repair_site := 0
			if str(mi.name) == "COL_R23_NanquSidewalk":
				repair_site = 1
			elif str(mi.name).begins_with("COL_Terrain_200m") and paving:
				repair_site = 2
			var residence := false
			if wall:
				for id in ["809889622","809889624","1335306667","1413081560","A03","A04"]:
					if str(mi.name).begins_with("COL_B_"+id+"_"):
						residence = true
						break
			var key := "%s/%s/%s/%s" % [mat.get_instance_id(),repair_site,wall,residence]
			if not treated.has(key):
				var copy := mat.duplicate() as ShaderMaterial
				copy.set_shader_parameter("use_street_history", paving)
				if not shader_path.ends_with("/frontage_surface_r24.gdshader"):
					copy.set_shader_parameter("repair_aggregate", preload("res://assets/chongqing_district_concrete_floor_worn_001_diff_2k.jpg"))
					copy.set_shader_parameter("repair_site",repair_site)
					if repair_site==2:
						copy.set_shader_parameter("courtyard_wear",preload("res://assets/courtyard_grade/footwear.png"))
						copy.set_shader_parameter("shoulder_gradient",preload("res://assets/district_age/shoulder_gradient.png"))
						copy.set_shader_parameter("district_footpaths",preload("res://assets/district_age/footpaths.png"))
					if wall:copy.set_shader_parameter("residential_age",residence)
					copy.set_shader_parameter("use_wall_toe", wall)
					if wall:
						copy.set_shader_parameter("support_heights",preload("res://assets/street_use_r24/support_heights.png"))
				copy.set_shader_parameter("street_history", USE_MAP)
				treated[key] = copy
			if mi.material_override:
				mi.material_override = treated[key]
			else:
				mi.set_surface_override_material(surface, treated[key])
			if wall:
				stats.facades += 1
			else:
				stats.paving += 1
	var workday := load(PROPS) as PackedScene
	if workday:
		city.add_child(workday.instantiate())
		stats.workday = true
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/street_use_r24/layout.json"))
	stats["resident_pots"] = place_resident_pots(city,layout.plants)
	var solids := StaticBody3D.new()
	solids.name = "WorkdayFurniture"
	city.add_child(solids)
	solids.add_to_group("workday_furniture")
	for item in layout.solids:
		var box := BoxShape3D.new()
		box.size = Vector3(item["size"][0],item["size"][1],item["size"][2])
		var collider := CollisionShape3D.new()
		collider.shape = box
		solids.add_child(collider)
		collider.global_position = Vector3(item.at[0],item.at[1],item.at[2])
	stats["furniture_volumes"] = solids.get_child_count()
	print("CQ_STREET_USE ", stats)
	return stats



static func place_resident_pots(city: Node3D, sites: Array) -> int:
	var sources: Array[MeshInstance3D] = []
	var bounds := AABB()
	for index in 3:
		var donor := city.find_child("B_809889623_market_Interior_asset_0_%02d" % index, true, false) as MeshInstance3D
		if not donor or not donor.mesh:
			push_error("Missing resident garden plant donor %s" % index)
			return 0
		var part := donor.global_transform * donor.get_aabb()
		bounds = part if sources.is_empty() else bounds.merge(part)
		sources.append(donor)
	var foot := bounds.get_center()
	foot.y = bounds.position.y
	for site in sites:
		var axes := Basis(Vector3.UP,float(site.yaw)).scaled(Vector3.ONE*float(site.scale))
		var base := Vector3(site.at[0],site.at[1],site.at[2])
		var location := Transform3D(axes,base-axes*foot)
		for donor in sources:
			var plant := MeshInstance3D.new()
			plant.name = "ResidentGardenPlant"
			plant.mesh = donor.mesh
			plant.visibility_range_end = 40.0
			plant.visibility_range_end_margin = 2.0
			plant.material_override = donor.material_override
			for face in donor.mesh.get_surface_count():
				plant.set_surface_override_material(face,donor.get_surface_override_material(face))
			city.add_child(plant,true)
			plant.global_transform = location*donor.global_transform
	return sites.size()
