extends SceneTree
func _initialize(): call_deferred("go")
func go():
	var m=load("res://main.tscn").instantiate()
	root.add_child(m)
	while not m.gameplay:await physics_frame
	var g=m.gameplay
	print("SITES shop=",g.shop.global_position," owner=",g.shopkeeper.global_transform," bag=",g.shopkeeper.food_end," door=",g.destination.global_position)
	for target in g.manager.targets:
		if target.interaction_id.begins_with("doorbell.A04"): print("BELL ",target.global_position)
	for pose in [[Vector3(-29.3,11.8,55.2),-PI/2],[Vector3(-25.4,14.4,36.95),0.]]:
		var floor_y:Vector3=g._grounded(pose[0])
		for side in [-1.,1.]:
			for z in [.38,.60,.85]:
				var p:Vector3=floor_y+Basis(Vector3.UP,pose[1])*Vector3(side*.50,0,z)
				print("BOX_FEET ",floor_y," side ",side," z ",z," feet ",g._grounded(p))
	quit()
