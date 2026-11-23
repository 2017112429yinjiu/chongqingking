@tool
extends RefCounted

const ROOT := "res://assets/terrace_gardens/"
const FLOOR := preload("res://assets/chongqing_district_concrete_floor_worn_001_diff_2k.jpg")
const GRIT := preload("res://assets/chongqing_district_concrete_floor_worn_001_nor_gl_2k.jpg")

static func finishes()->Dictionary:
	var paving:=ShaderMaterial.new()
	paving.shader=preload("res://shaders/terrace_grade_r24.gdshader")
	paving.set_shader_parameter("stone",FLOOR)
	paving.set_shader_parameter("terrace_grit",GRIT)
	paving.set_shader_parameter("terrace_normals",load(ROOT+"normals.png"))
	var result:={"Terrace21_floor":paving}
	for slot:String in ["mortar","coping_a","coping_b","coping_c","soil"]:
		var surface:=StandardMaterial3D.new()
		var soil:=slot=="soil"
		var tones:={"mortar":Color(.88,.85,.79),"coping_a":Color(.87,.81,.70),"coping_b":Color(.78,.73,.66),"coping_c":Color(.90,.83,.74),"soil":Color(.54,.47,.37)}
		surface.albedo_color=tones[slot]
		surface.albedo_texture=preload("res://assets/chongqing_district_leaf_scattered_gravel_diff_2k.jpg") if soil else FLOOR
		surface.normal_enabled=true
		surface.normal_texture=preload("res://assets/chongqing_district_leaf_scattered_gravel_nor_gl_2k.jpg") if soil else GRIT
		if slot=="mortar":
			surface.albedo_texture=preload("res://assets/chongqing_district_brick_wall_08_diff_2k.jpg")
			surface.normal_texture=preload("res://assets/chongqing_district_brick_wall_08_nor_gl_2k.jpg")
		surface.normal_scale=.57 if soil else .32
		surface.roughness=.94
		surface.uv1_scale=Vector3(.65,.65,.65) if soil else Vector3(.91,.91,.91)
		result["Garden21_"+slot]=surface
	var wall:=StandardMaterial3D.new()
	wall.albedo_texture=preload("res://assets/chongqing_district_stone_wall_05_diff_2k.jpg")
	wall.normal_texture=preload("res://assets/chongqing_district_stone_wall_05_nor_gl_2k.jpg")
	wall.normal_enabled=true
	wall.normal_scale=.48
	wall.roughness=.92
	wall.uv1_scale=Vector3(.51,.51,.51)
	result["Terrace21_retaining"]=wall
	return result

static func add_plants(city:Node3D,layer:Node3D,plants:Array,missing:Array)->void:
	var groups:={}
	var donors:={}
	for patch:Dictionary in plants:
		var placement:=preload("res://scripts/neighborhood_r24.gd")._matrix(patch.transform)
		for key:String in patch.donors:
			if not donors.has(key):donors[key]=city.find_child(key,true,false)
			var source:=donors[key] as MeshInstance3D
			if not source or not source.mesh:
				if not missing.has(key):missing.append(key)
				continue
			if not groups.has(key):groups[key]=[]
			groups[key].append(layer.global_transform.affine_inverse()*placement*source.global_transform)
	for key:String in groups:
		var source:MeshInstance3D=donors[key]
		var multi:=MultiMesh.new()
		multi.transform_format=MultiMesh.TRANSFORM_3D
		multi.mesh=source.mesh
		multi.instance_count=groups[key].size()
		for i in groups[key].size():multi.set_instance_transform(i,groups[key][i])
		var instance:=MultiMeshInstance3D.new()
		instance.name="TerracePlant_"+key
		instance.multimesh=multi
		# Each selected scan part has one surface, including the potted plant foliage without its pot.
		instance.material_override=source.get_active_material(0)
		instance.cast_shadow=source.cast_shadow
		instance.visibility_range_end=76. if key.begins_with("Planted_tree") else 44.
		instance.visibility_range_end_margin=5.
		layer.add_child(instance)
