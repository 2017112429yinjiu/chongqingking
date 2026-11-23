extends SceneTree

const RADII := [.14,.28,.42,.56,.70,.84]

func _initialize()->void:
	call_deferred("survey")

func supports(space:PhysicsDirectSpaceState3D, at:Vector3, ref_y:float, route:String, capsule:Shape3D, along:Vector3) -> bool:
	for axis in [-.17,0.,.17]:
		var foot:=at + along * float(axis)
		var query:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.24,foot-Vector3.UP*.24,1)
		var hit:=space.intersect_ray(query)
		if hit.is_empty() or hit.normal.y<.92 or absf(hit.position.y-ref_y)>.10:return false
		var surface:=str(hit.collider.get_parent().name)
		if route=="promenade" and surface!="COL_R23_NanquSidewalk":return false
		if not (surface.begins_with("COL_") or surface.begins_with("Walk_details_")) or "Road_" in surface or "Stairs" in surface:return false
	var shape:=PhysicsShapeQueryParameters3D.new()
	shape.shape=capsule
	shape.collision_mask=1
	shape.transform.origin=at+Vector3.UP*.92
	return space.intersect_shape(shape,1).is_empty()

func survey()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	var capsule:=CapsuleShape3D.new()
	capsule.radius=.255
	capsule.height=1.63
	var result:Dictionary={}
	for route:String in ["market_apron","promenade"]:
		var lane:Dictionary=game.street_block.walking_lanes[route]
		var limits:Dictionary={}
		for direction:String in ["forward","backward"]:
			var points:Array=lane[direction]
			var allowances:Array=[]
			for i in points.size():
				var p=game.street_block._v(points[i])
				var delta:Vector3=game.street_block._v(points[mini(points.size()-1,i+1)])-game.street_block._v(points[maxi(0,i-1)])
				delta.y=0.
				var along:=delta.normalized()*(1. if direction=="forward" else -1.)
				var side:=along.cross(Vector3.UP).normalized()
				var pair=[]
				for sign_value:float in [-1.,1.]:
					var limit:=0.
					for value:float in RADII:
						# Sample the outside supporting foot too, before authorising the torso centre.
						if not supports(space,p+side*(value+.13)*sign_value,p.y,route,capsule,along):break
						limit=value
					pair.append(limit)
				allowances.append(pair)
			limits[direction]=allowances
		result[route]=limits
	var folder:String=OS.get_cmdline_user_args()[-1]
	FileAccess.open(folder+"/passing_space.json",FileAccess.WRITE).store_string(JSON.stringify(result))
	print("MARKET16_PASSING_SURVEY ",result.keys())
	quit()
