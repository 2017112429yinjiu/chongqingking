extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var actor: Node3D=preload("res://scripts/shopkeeper.gd").new()
	root.add_child(actor)
	var seen: Dictionary={}
	for mesh: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
		for i in range(mesh.mesh.get_surface_count()):
			var mat: StandardMaterial3D=mesh.get_active_material(i)
			if seen.has(mat.resource_name):continue
			seen[mat.resource_name]={"albedo":str(mat.albedo_color),"vertex_color":mat.vertex_color_use_as_albedo,"normal_enabled":mat.normal_enabled,"normal_scale":mat.normal_scale,"roughness":mat.roughness,"alpha":mat.transparency,"textures":{}}
			for kind: String in ["albedo_texture","roughness_texture","normal_texture"]:
				var tex: Texture2D=mat.get(kind)
				if tex:seen[mat.resource_name].textures[kind]={"size":str(tex.get_size()),"path":tex.resource_path}
	FileAccess.open("res://verification_r18/material_import.json",FileAccess.WRITE).store_string(JSON.stringify(seen,"\t"))
	print("MATERIAL_IMPORT ",JSON.stringify(seen));quit()
