extends SceneTree
func _initialize()->void:call_deferred("bake")
func bake()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var vertices:=PackedVector3Array();var indices:=PackedInt32Array();var accepted={}
	for obj:MeshInstance3D in game.get_node("City").find_children("COL_B_*","MeshInstance3D",true,false):
		var label:=str(obj.name)
		if not obj.is_visible_in_tree() or not obj.mesh:continue
		if not ("_plaster_" in label or "_brick_" in label or label.ends_with("_tile") or label.ends_with("_concrete")):continue
		var bounds:AABB=obj.global_transform*obj.get_aabb()
		var mesh_faces:=obj.mesh.get_faces()
		var triangles:=0
		for i in range(0,mesh_faces.size(),3):
			var x:=obj.to_global(mesh_faces[i]);var y:=obj.to_global(mesh_faces[i+1]);var z:=obj.to_global(mesh_faces[i+2])
			var normal:Vector3=(y-x).cross(z-x)
			if normal.length_squared()<.90 or absf(normal.normalized().y)>.15:continue
			var center:Vector3=(x+y+z)/3.
			var inside:=bounds.get_center()-center;inside.y=0.
			var inset:=inside.normalized()*.018
			for point:Vector3 in [x,y,z]:
				indices.append(vertices.size());vertices.append(point.lerp(center,.022)+inset)
			triangles+=1
		if triangles>0:accepted[label]=triangles
	var oc:=ArrayOccluder3D.new();oc.set_arrays(vertices,indices)
	var folder:String=OS.get_cmdline_user_args()[-1]
	var err:=ResourceSaver.save(oc,folder+"/interior_wall_faces.res")
	FileAccess.open(folder+"/bake.json",FileAccess.WRITE).store_string(JSON.stringify({"build":game.art_profile.art_revision,"source_meshes":accepted,"triangles":indices.size()/3},'  '))
	print("ROOM15_OCC_BAKE ",err," ",accepted.size()," ",indices.size()/3)
	quit(err)
