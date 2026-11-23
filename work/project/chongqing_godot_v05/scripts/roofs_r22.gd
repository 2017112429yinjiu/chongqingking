extends RefCounted

const MODEL := "res://assets/roofs_r22/roofs_and_breakfast.glb"
const LAYOUT := "res://assets/roofs_r22/layout.json"

static func install(city: Node3D) -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	var layer := (load(MODEL) as PackedScene).instantiate() as Node3D
	layer.name = "RoofsAndBreakfastR22"
	city.add_child(layer)
	var canvas := layer.find_child("R22_Breakfast_canvas",true,false) as MeshInstance3D
	var cloth := canvas.get_active_material(0) as StandardMaterial3D
	var breeze := ShaderMaterial.new()
	breeze.shader = preload("res://shaders/breakfast_canvas_r22.gdshader")
	breeze.set_shader_parameter("fabric",cloth.albedo_texture)
	canvas.set_surface_override_material(0,breeze)
	return {"layer_sha256":FileAccess.get_sha256(MODEL),"layout_sha256":FileAccess.get_sha256(LAYOUT),
		"decks":plan.decks.size(),"stations":plan.stations.size(),"sockets":plan.wall_sockets.size(),
		"canvas_shader_sha256":FileAccess.get_sha256("res://shaders/breakfast_canvas_r22.gdshader")}
