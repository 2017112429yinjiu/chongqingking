@tool
extends RefCounted

const LAYER := "res://assets/lane_connection_r24/junction.glb"
const PLAN := "res://assets/lane_connection_r24/layout.json"

static func paver(landing:bool)->ShaderMaterial:
	var surface:=ShaderMaterial.new()
	surface.shader=preload("res://shaders/lane_pavers_r24.gdshader")
	surface.set_shader_parameter("cement",preload("res://assets/chongqing_district_concrete_floor_worn_001_diff_2k.jpg"))
	surface.set_shader_parameter("grain",preload("res://assets/chongqing_district_concrete_floor_worn_001_nor_gl_2k.jpg"))
	surface.set_shader_parameter("landing",landing)
	return surface

static func apply_finish(visual:MeshInstance3D,original:Material)->void:
	visual.material_override=null
	for i in visual.mesh.get_surface_count():
		var slot:=visual.mesh.surface_get_material(i)
		visual.set_surface_override_material(i,paver(true) if slot and slot.resource_name=="East17_CourtLanding" else original)

static func install(city: Node3D, editor_preview := false) -> Dictionary:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var library := (load(LAYER) as PackedScene).instantiate() as Node3D
	var preview_library:Node3D
	if editor_preview:preview_library=(load("res://assets/lane_connection_r24/editor/openings.glb") as PackedScene).instantiate()
	var original_drawings:Array=[]
	var preview_drawings:Array=[]
	var missing: Array[String] = []
	var replacements := 0
	var additions := 0
	var concrete_source := city.find_child("COL_Walk_East_photo_alley_step_concrete",true,false) as MeshInstance3D
	var stone:Material = concrete_source.get_active_material(0) if concrete_source else null
	var foundation := city.find_child("COL_R23_PathFoundations",true,false) as MeshInstance3D
	var support:Material = foundation.get_active_material(0) if foundation else stone
	for name_key: String in plan.source_nodes:
		var target := city.find_child(name_key,true,false) as MeshInstance3D
		var source := library.find_child(name_key,true,false) as MeshInstance3D
		if editor_preview:source=preview_library.find_child("Preview_"+name_key,true,false) as MeshInstance3D
		if not target or not source:
			if not editor_preview:missing.append(name_key)
			continue
		if editor_preview:
			# These unowned, internal drawing proxies never become editable scene overrides.
			var visual := MeshInstance3D.new()
			visual.mesh=source.mesh
			apply_finish(visual,target.get_active_material(0))
			city.add_child(visual,false,Node.INTERNAL_MODE_BACK)
			visual.global_transform=target.global_transform
			RenderingServer.instance_set_visible(target.get_instance(),false)
			original_drawings.append(target)
			preview_drawings.append(visual)
		else:
			var finish:=target.get_active_material(0)
			target.mesh=source.mesh
			apply_finish(target,finish)
		replacements+=1
	for name_key: String in plan.new_nodes:
		var source:=library.find_child(name_key,true,false) as MeshInstance3D
		if not source:missing.append(name_key);continue
		source.owner=null
		source.get_parent().remove_child(source)
		if editor_preview:
			city.add_child(source,false,Node.INTERNAL_MODE_BACK)
			preview_drawings.append(source)
		else:city.add_child(source)
		if name_key=="COL_East17_TerraceSteps":
			var dressing:=ShaderMaterial.new()
			dressing.shader=preload("res://shaders/lane_steps_r24.gdshader")
			dressing.set_shader_parameter("stone",preload("res://assets/district_r21/terraces_washed_sandstone.jpg"))
			dressing.set_shader_parameter("rough",preload("res://assets/district_r21/terraces_sandstone_cracks_rough_2k.png"))
			dressing.set_shader_parameter("grain",preload("res://assets/district_r21/terraces_sandstone_cracks_nor_gl_2k.jpg"))
			source.material_override=dressing
		if name_key=="COL_East17_CourtyardPaving":
			source.material_override=paver(false)
		if name_key in ["COL_East17_LandingReturns","COL_East17_ShoulderReturns"] and support:source.material_override=support
		additions+=1
	library.free()
	if editor_preview:
		preview_library.free()
		return {"originals":original_drawings,"drawings":preview_drawings,"replaced":replacements,"added":additions}
	return {"replaced":replacements,"added":additions,"missing":missing}
