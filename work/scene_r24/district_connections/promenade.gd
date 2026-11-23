extends SceneTree
func _initialize()->void:call_deferred("inspect_route")
func inspect_route()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var space:=root.world_3d.direct_space_state
	for i in range(33,49):
		var t:=i*.42
		var p:Vector3=game.street_block.walk_position("promenade",t,1)
		var row: Array=[i,[p.x,p.y,p.z]]
		for dz in [-.21,0.,.21]:
			var at:Vector3=p+Vector3(0,0,dz)
			var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*2,at-Vector3.UP*1.8,1))
			if h:row.append([h.position.y,str(h.collider.get_parent().name),h.normal.y])
		print("SIDE_PROBE ",JSON.stringify(row))
	quit()
