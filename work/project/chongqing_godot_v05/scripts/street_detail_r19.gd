extends RefCounted
## Additive authored Blender layer, exact replacement list and PBR refinements.
static func apply(city: Node3D, profile: Dictionary) -> Dictionary:
	if not bool(profile.get("street_r19", {}).get("enabled", false)):
		return {"enabled":false}
	var path: String = "res://assets/street_r19/street_life.glb"
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/street_r19/manifest.json"))
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		push_error("R19 street layer failed to load")
		return {"enabled":false,"error":"load_failed"}
	var replaced: Array[String] = []
	for mesh: Node in city.find_children("*", "MeshInstance3D", true, false):
		if spec.hide_city_objects.has(str(mesh.name)):
			mesh.visible = false
			replaced.append(str(mesh.name))
	var layer: Node3D = packed.instantiate()
	layer.name="StreetLifeR19"
	city.add_child(layer)
	for light_spec: Dictionary in spec.get("practical_lights",[]):
		# The covered canopy fixture throws light downwards. A single shadow
		# projection avoids six cubemap faces for a light under an opaque roof.
		var light:=SpotLight3D.new()
		light.position=Vector3(light_spec.position[0],light_spec.position[1],light_spec.position[2])
		light.rotation_degrees.x=-90.0
		light.light_color=Color(light_spec.color[0],light_spec.color[1],light_spec.color[2])
		light.light_energy=light_spec.energy
		light.spot_range=light_spec.range
		light.spot_angle=65.0
		light.shadow_enabled=true
		light.shadow_bias=.03
		light.shadow_normal_bias=.35
		layer.add_child(light)
	return {"enabled":true,"asset":path,"sha256":FileAccess.get_sha256(path),"manifest_sha256":FileAccess.get_sha256("res://assets/street_r19/manifest.json"),"replaced":replaced,"source_revision":spec.revision}

static func surfaces(city: Node3D, profile: Dictionary) -> Dictionary:
	var result: Dictionary = {"surfaces":0,"materials":[]}
	if not bool(profile.get("street_r19",{}).get("surfaces",false)):return result
	var cache: Dictionary = {}
	var sky_fields: bool = profile.get("lane_r20", false)
	var weathered: bool=profile.get("district_r21",false)
	for mesh: Node in city.find_children("*", "MeshInstance3D", true, false):
		if mesh.mesh==null or not mesh.visible:continue
		for i in range(mesh.mesh.get_surface_count()):
			var original: Material=mesh.get_active_material(i)
			if not original is BaseMaterial3D:continue
			var n: String=original.resource_name
			var ground: bool=n in ["CQ03_PBR_pavement","CQ03_PBR_yard_concrete","CQ03_PBR_step_concrete","CQ03_PBR_paving_slab","R20_Dressed_stone"]
			var plaster: bool=n.begins_with("CQ03_PBR_plaster")
			var local_wall: bool = sky_fields and ("1413081560" in str(mesh.name) or "1335306665" in str(mesh.name) or "A01_noodle" in str(mesh.name)) and (n.begins_with("CQ03_PBR_stone") or n.begins_with("CQ03_PBR_tile"))
			var shell: bool=weathered and str(mesh.name).begins_with("COL_B_") and (n.begins_with("CQ03_PBR_tile") or n.begins_with("CQ03_PBR_brick") or n.begins_with("CQ03_PBR_stone") or n.begins_with("CQ03_PBR_concrete"))
			if not ground and not plaster and not local_wall and not shell:continue
			var colors: bool=(mesh.mesh.surface_get_format(i)&Mesh.ARRAY_FORMAT_COLOR)!=0
			var key: String=n+str(colors)
			if not cache.has(key):
				var mat:=ShaderMaterial.new()
				mat.shader=load("res://shaders/street_surface_r19.gdshader")
				mat.resource_name="R19_"+n
				mat.set_shader_parameter("albedo_map",original.albedo_texture)
				mat.set_shader_parameter("base_color",original.albedo_color)
				mat.set_shader_parameter("normal_map",original.normal_texture)
				mat.set_shader_parameter("has_normal",original.normal_enabled and original.normal_texture!=null)
				mat.set_shader_parameter("normal_strength",original.normal_scale)
				mat.set_shader_parameter("rough_map",original.roughness_texture)
				var channel:=Vector4.ZERO
				if original.roughness_texture_channel<4:channel[original.roughness_texture_channel]=1.
				else:channel=Vector4(.33333,.33333,.33333,0)
				mat.set_shader_parameter("rough_channel",channel)
				mat.set_shader_parameter("roughness_factor",original.roughness)
				mat.set_shader_parameter("uv_scale",original.uv1_scale)
				mat.set_shader_parameter("uv_offset",original.uv1_offset)
				mat.set_shader_parameter("vertex_tint",colors)
				mat.set_shader_parameter("surface_kind",0. if ground else (1. if plaster else 2.))
				if sky_fields:
					mat.set_shader_parameter("use_sky_field", true)
					mat.set_shader_parameter("shop_sky", load("res://assets/lane_r20/shop_sky.png"))
					mat.set_shader_parameter("alley_sky", load("res://assets/lane_r20/alley_sky.png"))
				cache[key]=mat
			mesh.set_surface_override_material(i,cache[key])
			result.surfaces+=1
	result.materials=cache.keys()
	return result
