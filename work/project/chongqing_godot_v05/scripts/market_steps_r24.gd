extends RefCounted

const STAIR_NAME := "COL_R24_MarketStairs_R24_step_stone"
const APRON_NAME := "COL_R23_NanquUpperApron"

static func install(city: Node3D) -> Dictionary:
	var dressed := ShaderMaterial.new()
	dressed.shader = preload("res://shaders/market_sandstone_r24.gdshader")
	dressed.set_shader_parameter("rock", preload("res://assets/district_r21/terraces_washed_sandstone.jpg"))
	dressed.set_shader_parameter("grain_normal", preload("res://assets/district_r21/terraces_sandstone_cracks_nor_gl_2k.jpg"))
	dressed.set_shader_parameter("roughness_scan", preload("res://assets/district_r21/terraces_sandstone_cracks_rough_2k.png"))
	var coping := dressed.duplicate() as ShaderMaterial
	coping.set_shader_parameter("coping", true)
	var layer := (load("res://assets/market_steps_r24/market.glb") as PackedScene).instantiate() as Node3D
	var switches := {}
	for key: String in [STAIR_NAME, APRON_NAME]:
		var source := layer.find_child(key, true, false) as MeshInstance3D
		var target := city.find_child(key, true, false) as MeshInstance3D
		if not source or not target:
			push_error("Missing original market entrance mesh " + key)
			continue
		var original := target.get_active_material(0)
		var finishes: Array[String] = []
		target.material_override = null
		target.mesh = source.mesh
		for slot in target.mesh.get_surface_count():
			var mat := target.mesh.surface_get_material(slot)
			var finish := mat.resource_name
			if finish == "Market16_CutSandstone":
				mat = coping if key == APRON_NAME else dressed
			elif key == APRON_NAME:
				mat = original
			target.set_surface_override_material(slot, mat)
			finishes.append(finish)
		switches[key] = finishes
	layer.free()
	return switches
