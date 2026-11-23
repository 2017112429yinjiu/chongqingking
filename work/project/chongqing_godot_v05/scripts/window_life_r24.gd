extends RefCounted

const FOLDER := "res://assets/rooms_r24/"
const LIGHT_LAYER := 1 << 15

static func vector(row:Array) -> Vector3:
	return Vector3(row[0],row[1],row[2])

static func install(city:Node3D, feather_stains:bool) -> Dictionary:
	var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"layout.json"))
	var rooms:Node3D=(load(FOLDER+"rooms.glb") as PackedScene).instantiate()
	rooms.name="WindowRooms15"
	city.add_child(rooms)
	var new_meshes:=rooms.find_children("*","MeshInstance3D",true,false)
	var material_receivers:=0
	for m:MeshInstance3D in city.find_children("IR_B_*_Interiors_*","MeshInstance3D",true,false):
		if str(m.name).begins_with("IR_B_A01_noodle_") or str(m.name).begins_with("IR_B_A04_courtyard_home_"):
			m.layers|=LIGHT_LAYER
			material_receivers+=1
	for m:MeshInstance3D in new_meshes:
		m.layers|=LIGHT_LAYER
		m.visibility_range_end=48.
		m.visibility_range_end_margin=7.
		m.visibility_range_fade_mode=GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
	for entry in layout.lights:
		var light:=SpotLight3D.new()
		rooms.add_child(light)
		light.position=vector(entry.at)
		light.look_at(vector(entry.aim),Vector3.UP)
		light.light_color=Color(1.,.946,.865)
		light.light_energy=entry.energy
		light.light_cull_mask=LIGHT_LAYER
		light.spot_range=3.25
		light.spot_angle=54.
		light.spot_angle_attenuation=.72
		light.distance_fade_enabled=true
		light.distance_fade_begin=21.
		light.distance_fade_length=9.
	var patina_count:=0
	if feather_stains:
		var coating:=ShaderMaterial.new()
		coating.shader=preload("res://shaders/wall_patina_r24.gdshader")
		coating.set_shader_parameter("stain",preload("res://assets/chongqing_district_moss_grime_diff.png"))
		var masks:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FOLDER+"patina.json"))
		var donor_root:Node3D=(load(FOLDER+"patina.glb") as PackedScene).instantiate()
		city.add_child(donor_root)
		for pair in masks.donors:
			var target:=city.find_child(pair[0],true,false) as MeshInstance3D
			var source:=donor_root.find_child(pair[1],true,false) as MeshInstance3D
			if target and source:
				target.mesh=source.mesh
				target.global_transform=source.global_transform
				target.material_override=coating
				target.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				patina_count+=1
		donor_root.free()
	return {"furnishings":new_meshes.size(),"lights":layout.lights.size(),"existing_room_meshes":material_receivers,"patina_batches":patina_count}
