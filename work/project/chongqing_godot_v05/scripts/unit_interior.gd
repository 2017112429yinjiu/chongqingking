@tool
extends RefCounted
## One continuous pair of street entrances and two residential addresses.
const TITLE := "山城里小院 · 一单元"
const LANDING_SHIFT := Vector3(-9.0,3.45,0)
const COURT := Vector3(-51.3,16.44,19.5)
const LANDING := Vector3(-62.25,19.89,19.62)
const DOOR_POINTS := [Vector3(-64.18,21.20,19.70),Vector3(-62.91,21.20,13.58)]
const SHELVES := [Vector3(-64.142,20.78,20.38),Vector3(-62.927,20.78,14.62)]
const ADDRESSES := ["一单元 201","一单元 202"]

static func entrance_route(to:Vector3)->PackedVector3Array:
	return PackedVector3Array([COURT,Vector3(-54.9,16.44,19.50),LANDING,to])

static func downstairs(to:Vector3)->PackedVector3Array:
	return PackedVector3Array([LANDING,Vector3(-54.9,16.44,19.50),COURT,to])

static func finishes()->Dictionary:
	var result:={}
	for key:String in ["plaster","dado","terrazzo","tread","edge","metal","lamp","maroon","enamel","brass","conduit"]:
		var m:=StandardMaterial3D.new()
		var tint:Color={"plaster":Color("c9c0ac"),"dado":Color("788e80"),"terrazzo":Color("adaba2"),"tread":Color("b0ada2"),"edge":Color("807c71"),"metal":Color("52655d"),"lamp":Color("ece8d9"),"maroon":Color("66514b"),"enamel":Color("dad4ba"),"brass":Color("b59b70"),"conduit":Color("878b84")}[key]
		m.albedo_color=tint
		m.roughness=.84
		var stem:=""
		if key in ["plaster","dado"]:stem="res://assets/chongqing_district_plastered_wall_04"
		elif key in ["terrazzo","tread","edge"]:stem="res://assets/chongqing_district_concrete_floor_worn_001"
		if stem!="":
			var resolution:="1k" if key in ["plaster","dado"] else "2k"
			m.albedo_texture=load(stem+"_diff_"+resolution+".jpg")
			m.normal_enabled=true
			m.normal_texture=load(stem+"_nor_gl_"+resolution+".jpg")
			m.normal_scale=.20
			m.uv1_scale=Vector3(.59,.59,.59)
		if key in ["maroon","metal"]:
			m.albedo_texture=preload("res://assets/chongqing_district_rusty_painted_metal_diff_2k.jpg")
			m.normal_enabled=true
			m.normal_texture=preload("res://assets/chongqing_district_rusty_painted_metal_nor_gl_2k.jpg")
			m.normal_scale=.19
			m.uv1_scale=Vector3(.53,.53,.53)
		if key=="lamp":
			m.emission_enabled=true
			m.emission=Color("fff0c8")
			m.emission_energy_multiplier=1.7
		if key in ["metal","brass","conduit"]:m.metallic=.44
		result["R18_unit22_"+key]=m
	var notices:=StandardMaterial3D.new()
	notices.albedo_texture=preload("res://assets/district_age/wall_prints.png")
	notices.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	notices.alpha_scissor_threshold=.18
	notices.roughness=.92
	result["R18_unit22_paper"]=notices
	return result

static func furnish(root:Node3D)->void:
	for spec:Array in [[Vector3(-54.95,18.82,19.5),3.3],[Vector3(-58.10,20.35,19.5),3.6],[Vector3(-62.9,22.20,19.55),3.9],[Vector3(-62.17,22.18,13.85),4.6]]:
		var light:=OmniLight3D.new()
		light.position=spec[0]
		light.omni_range=spec[1]
		light.light_color=Color("fff0d7")
		light.light_energy=.83
		light.distance_fade_enabled=true
		light.distance_fade_begin=18
		light.distance_fade_length=10
		root.add_child(light)
	for spec:Array in [
		["一单元",Vector3(-52.963,19.35,19.51),PI/2,.35,.18],
		["201",Vector3(-64.18,21.62,19.51),PI/2,.25,.13],
		["202",Vector3(-62.965,21.62,13.69),PI/2,.25,.13],
		["1F",Vector3(-54.80,18.17,18.42),0.0,.28,.17],
		["2F",Vector3(-63.50,21.58,18.44),0.0,.28,.17],
		["一单元  ·  二楼",Vector3(-62.15,22.21,8.965),PI,.62,.17]]:
		var plaque:=MeshInstance3D.new()
		var box:=BoxMesh.new()
		box.size=Vector3(spec[3],spec[4],.015)
		plaque.mesh=box
		var blue:=StandardMaterial3D.new()
		blue.albedo_color=Color("304e63")
		blue.roughness=.51
		plaque.material_override=blue
		root.add_child(plaque)
		plaque.position=spec[1]
		plaque.rotation.y=spec[2]
		var letters:=Label3D.new()
		letters.font=preload("res://assets/fonts/first_shift.otf")
		letters.text=spec[0]
		letters.pixel_size=.00165
		letters.font_size=45
		letters.outline_size=0
		letters.modulate=Color("ece3cb")
		plaque.add_child(letters)
		letters.position.z=.009
