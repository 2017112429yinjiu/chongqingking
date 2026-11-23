extends RefCounted

const MODEL = "res://assets/lane_r20/upper_lane.glb"
const FIELD_FILES = ["res://assets/lane_r20/shop_sky.png", "res://assets/lane_r20/alley_sky.png"]

static func install(city: Node3D, still_frame: bool) -> Dictionary:
	var scene := load(MODEL) as PackedScene
	if scene == null:
		push_error("Upper stair lane could not load")
		return {"enabled": false}
	var lane := scene.instantiate() as Node3D
	lane.name = "UpperLaneR20"
	city.add_child(lane)
	for piece in ["R20_Work_shirt_indigo", "R20_Striped_hand_towel_cotton"]:
		var cloth := lane.find_child(piece, true, false) as MeshInstance3D
		var original := cloth.get_active_material(0) as BaseMaterial3D
		var fabric := ShaderMaterial.new()
		fabric.shader = preload("res://shaders/hanging_cotton_r20.gdshader")
		fabric.set_shader_parameter("dye", original.albedo_color)
		fabric.set_shader_parameter("phase", 1.3 if piece.contains("shirt") else .2)
		fabric.set_shader_parameter("still_frame", still_frame)
		cloth.set_surface_override_material(0, fabric)
	var fields := {}
	for path: String in FIELD_FILES:
		fields[path] = FileAccess.get_sha256(path)
	return {"enabled": true, "model_sha256": FileAccess.get_sha256(MODEL), "sky_sha256": fields}
