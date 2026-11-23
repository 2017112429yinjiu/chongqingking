extends SceneTree
func _initialize(): call_deferred("probe")
func probe():
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.gameplay: await physics_frame
	await physics_frame
	var start=Vector3(-53.8,17.84,19.71)
	var end=start+Vector3.LEFT*2.
	for mi in main.find_children("*","MeshInstance3D",true,false):
		if not mi.mesh or not mi.is_visible_in_tree(): continue
		var a=mi.to_local(start)
		var b=mi.to_local(end)
		if not mi.get_aabb().grow(.001).intersects_segment(a,b):continue
		for surf in mi.mesh.get_surface_count():
			if mi.mesh.surface_get_primitive_type(surf)!=Mesh.PRIMITIVE_TRIANGLES:continue
			var data=mi.mesh.surface_get_arrays(surf)
			var v=data[Mesh.ARRAY_VERTEX]
			var indices=data[Mesh.ARRAY_INDEX]
			if v==null:continue
			var indexed=indices!=null and indices.size()>0
			var count=indices.size() if indexed else v.size()
			for i in range(0,count-2,3):
				var p=v[indices[i] if indexed else i]
				var q=v[indices[i+1] if indexed else i+1]
				var r=v[indices[i+2] if indexed else i+2]
				var hit=Geometry3D.segment_intersects_triangle(a,b,p,q,r)
				if hit!=null:
					var mat=mi.get_active_material(surf)
					print("DOOR_MESH ",mi.name," / ",mat.resource_name if mat else "-", " ",mi.to_global(hit))
	var hit=main.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end,1))
	print("DOOR_PHYS ",hit)
	quit()
