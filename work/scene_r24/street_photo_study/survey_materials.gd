extends SceneTree
func _initialize()->void:call_deferred("survey")
func survey()->void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null:await physics_frame
	var data: Array=[]
	for mesh:MeshInstance3D in main.get_node("City").find_children("*","MeshInstance3D",true,false):
		if not mesh.is_visible_in_tree() or not mesh.mesh:continue
		var box:=mesh.global_transform*mesh.get_aabb()
		if box.position.x>105 or box.end.x< -105 or box.position.z>105 or box.end.z< -105:continue
		var slots: Array=[]
		for i in mesh.mesh.get_surface_count():
			var mat:=mesh.get_active_material(i)
			if mat is ShaderMaterial:
				slots.append([mat.resource_name,mat.shader.resource_path if mat.shader else "",str(mat.get_shader_parameter("stairs"))])
			elif mat is BaseMaterial3D:
				slots.append([mat.resource_name,"Standard",mat.albedo_texture.resource_path if mat.albedo_texture else ""])
			else:slots.append(["","unknown",""])
		data.append([str(mesh.name),[box.position.x,box.position.y,box.position.z,box.size.x,box.size.y,box.size.z],slots])
	var args=OS.get_cmdline_user_args()
	var f=FileAccess.open(args[-1],FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	print("INSPECTED ",data.size())
	quit()

