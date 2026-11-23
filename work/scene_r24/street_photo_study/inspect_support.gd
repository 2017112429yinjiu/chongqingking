extends SceneTree
func _initialize()->void: call_deferred("inspect")
func inspect()->void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null: await physics_frame
	for delay in 3: await physics_frame
	var args=OS.get_cmdline_user_args()
	var points=JSON.parse_string(FileAccess.get_file_as_string(args[-2])).anchors
	var data=[]
	var space=main.get_world_3d().direct_space_state
	for pt in points:
		var x=float(pt.x)
		var z=-float(pt.blender_y)
		var y=float(pt.height)
		var q=PhysicsRayQueryParameters3D.create(Vector3(x,y+.82,z),Vector3(x,y-1.20,z))
		var excluded: Array[RID] = []
		for furnishing in get_nodes_in_group("workday_furniture"):
			excluded.append(furnishing.get_rid())
		q.exclude=excluded
		var h=space.intersect_ray(q)
		if h.is_empty():
			data.append({"item":pt.item,"x":x,"z":z,"miss":true})
		else:
			data.append({"item":pt.item,"x":x,"z":z,"height":h.position.y,"diff":h.position.y-y,"normal":[h.normal.x,h.normal.y,h.normal.z],"object":str(h.collider.get_parent().name)})
	FileAccess.open(args[-1],FileAccess.WRITE).store_string(JSON.stringify(data,"  "))
	print("CQ_SUPPORT_PROBES ",data.size())
	quit()

