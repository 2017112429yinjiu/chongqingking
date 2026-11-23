extends SceneTree
func _initialize()->void:call_deferred("sample")
func sample()->void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null:await physics_frame
	var rows=[]
	for node:MeshInstance3D in main.get_node("City").find_children("*","MeshInstance3D",true,false):
		if node.is_visible_in_tree() and node.mesh is ArrayMesh:
			var count=0
			for i in node.mesh.get_surface_count():count+=maxi(node.mesh.surface_get_array_index_len(i),node.mesh.surface_get_array_len(i))/3
			var b=node.global_transform*node.get_aabb()
			rows.append([count,str(node.name),b.get_longest_axis_size(),node.visibility_range_end,node.lod_bias,b.get_center().distance_to(Vector3(-20,18,24))])
	rows.sort_custom(func(a,b):return a[0]>b[0])
	FileAccess.open(OS.get_cmdline_user_args()[-1],FileAccess.WRITE).store_string(JSON.stringify(rows))
	quit()
