extends Node3D

const STREET_ASSET := "res://assets/street_finish_r24/street_finish.glb"
const STREET_INDEX := "res://assets/street_finish_r24/finish.json"
const LOCAL_FRAME := "../../scene_r24/city_frame_11864101/city_frame.glb"

func install(city: Node3D, include_local_frame: bool = true) -> Dictionary:
	var info := {"donors":0, "retired":0, "missing":[], "local_frame":false}
	var originals := {}
	for item in city.find_children("*","MeshInstance3D",true,false):
		originals[str(item.name).replace(".","_")] = item
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(STREET_INDEX))
	var packed := load(STREET_ASSET) as PackedScene
	var layer := packed.instantiate()
	add_child(layer)
	var zinc:=ShaderMaterial.new()
	zinc.shader=preload("res://shaders/court_canopy_r24.gdshader")
	for key in manifest.retire:
		var old := originals.get(key) as MeshInstance3D
		if old:
			old.hide()
			info.retired += 1
		else:
			info.missing.append(key)
	for item in layer.find_children("*","MeshInstance3D",true,false):
		var key := str(item.name)
		if key.ends_with("_Roof"):
			item.set_surface_override_material(0,zinc)
		if not manifest.donors.has(key):
			continue
		var target := originals.get(manifest.donors[key]) as MeshInstance3D
		if not target:
			info.missing.append(manifest.donors[key])
			continue
		var material := target.get_active_material(0)
		target.mesh = item.mesh
		target.global_transform = item.global_transform
		target.set_surface_override_material(0,material)
		item.free()
		info.donors += 1
	if not info.missing.is_empty():
		push_error("Street geometry missing source nodes %s" % [info.missing])
	if include_local_frame and OS.has_feature("editor"):
		var path := ProjectSettings.globalize_path("res://").path_join(LOCAL_FRAME).simplify_path()
		if FileAccess.file_exists(path):
			var doc := GLTFDocument.new()
			var state := GLTFState.new()
			if doc.append_from_file(path,state) == OK:
				var context := doc.generate_scene(state)
				if context:
					context.name = "LocalCityFrame"
					add_child(context)
					for mesh in context.find_children("*","MeshInstance3D",true,false):
						if not "_wall" in str(mesh.name):
							continue
						var original := mesh.get_active_material(0) as StandardMaterial3D
						if original:
							var facade:=ShaderMaterial.new()
							facade.shader=preload("res://shaders/city_envelope_r24.gdshader")
							facade.set_shader_parameter("plaster",original.albedo_color)
							mesh.set_surface_override_material(0,facade)
					info.local_frame = true
	return info

