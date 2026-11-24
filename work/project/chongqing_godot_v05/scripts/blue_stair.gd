@tool
extends RefCounted
static func finishes()->Dictionary:
	var enamel:=StandardMaterial3D.new()
	enamel.albedo_color=Color("819188")
	enamel.albedo_texture=preload("res://assets/chongqing_district_plastered_wall_04_diff_1k.jpg")
	enamel.normal_enabled=true
	enamel.normal_texture=preload("res://assets/chongqing_district_rusty_painted_metal_nor_gl_2k.jpg")
	enamel.normal_scale=.16
	enamel.metallic=.24
	enamel.roughness=.69
	enamel.uv1_scale=Vector3(.45,.45,.45)
	var timber:=StandardMaterial3D.new()
	timber.albedo_texture=preload("res://assets/chongqing_district_wood_table_worn_diff_2k.jpg")
	timber.albedo_color=Color("b79d87")
	timber.roughness=.71
	timber.uv1_scale=Vector3(.64,.64,.64)
	var pane:=StandardMaterial3D.new()
	pane.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	pane.albedo_color=Color(.67,.74,.72,.065)
	pane.roughness=.22
	return {"R18_blue24_blueiron":enamel,"R18_blue24_doorwood":timber,"R18_blue24_glass":pane}

static func furnish(root:Node3D)->void:
	var font:=preload("res://assets/fonts/first_shift.otf")
	var blue:=StandardMaterial3D.new()
	blue.albedo_color=Color("334f5d")
	blue.roughness=.68
	for row:Array in [
		["三楼住户　301",Vector3(-61.286,21.52,16.14),-PI/2,.95],
		["三楼　左转到户",Vector3(-54.795,24.50,17.50),-PI/2,1.03],
		["背巷出口",Vector3(-61.286,21.49,10.72),-PI/2,.56],
		["蓝砖楼　背巷门",Vector3(-84.85,19.65,8.877),PI,1.02],
		["上层连廊　折返上楼",Vector3(-82.72,22.08,17.785),PI,1.24],
		["四楼　过街连廊",Vector3(-80.45,25.46,9.317),0.,.98],
		["蓝砖楼　四层平台",Vector3(-77.968,26.85,14.46),PI/2,1.42],
		["下背巷　右转",Vector3(-81.395,25.38,14.41),PI/2,.81],
		["一单元　三楼",Vector3(-66.054,26.366,14.43),-PI/2,1.04],
		["一单元　下半层",Vector3(-65.60,25.38,15.330),PI,.96],
		["楼道灯已换　随手关窗",Vector3(-61.29,24.37,13.458),0.,.72],
		["301",Vector3(-58.834,24.62,14.08),-PI/2,.30]]:
		var plate:=MeshInstance3D.new()
		var box:=BoxMesh.new()
		box.size=Vector3(row[3],.195,.016)
		plate.mesh=box
		plate.material_override=blue
		root.add_child(plate)
		plate.position=row[1]
		plate.rotation.y=row[2]
		var words:=Label3D.new()
		words.font=font
		words.font_size=56
		words.pixel_size=.00190
		words.modulate=Color("f1e7cf")
		words.outline_size=0
		words.text=row[0]
		words.position.z=.0095
		plate.add_child(words)
	for light_at:Vector3 in [Vector3(-58.50,23.55,17.5),Vector3(-55.5,25.02,16.1),Vector3(-84.85,20.51,11.92),Vector3(-84.85,22.22,14.94),Vector3(-84,22.60,17.06),Vector3(-82.55,25.95,11.5),Vector3(-80.18,26.08,14.2),Vector3(-61,26.02,14.36)]:
		var lamp:=OmniLight3D.new()
		lamp.position=light_at
		lamp.light_color=Color("ffefda")
		lamp.light_energy=1.08
		lamp.omni_range=4.8
		lamp.distance_fade_enabled=true
		lamp.distance_fade_begin=19
		root.add_child(lamp)
