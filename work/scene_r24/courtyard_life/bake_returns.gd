extends SceneTree
func _initialize()->void:call_deferred("bake")

func bake()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	for i in 3:await physics_frame
	var block=game.street_block
	var space=game.get_world_3d().direct_space_state
	var capsule:=CapsuleShape3D.new()
	capsule.radius=.22;capsule.height=1.54
	var plan={};var failures=[];var verification={}
	for key in block.walking_lanes:
		plan[key]={}
		var length:float=block.routes[key].get_baked_length()
		for end_name in ["start","end"]:
			var from_sign:float=-1. if end_name=="start" else 1.
			var found:=false;var rejected=[]
			for delay in [0.,.45,1.05,1.65,2.2,2.9,3.75,4.7,5.5,6.4,7.2,8.5]:
				var done:float=delay+1.75;var count:=0;var clear:=true
				var last=Vector3.ZERO
				for i in range(ceili((done+.20)/.10)+1):
					var d=i*.10;var station:float=d if end_name=="start" else length-d
					var a=block.walk_position(key,station,from_sign);var b=block.walk_position(key,station,-from_sign)
					var pos:Vector3=a.lerp(b,smoothstep(delay,done,d))
					var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(pos+Vector3.UP*.45,pos-Vector3.UP*.70,1))
					if not hit or hit.normal.y<.64:clear=false;rejected.append([delay,d,"floor"]);break
					var body=PhysicsShapeQueryParameters3D.new();body.shape=capsule;body.transform.origin=hit.position+Vector3.UP*.94;body.collision_mask=1
					var obstacle=space.intersect_shape(body,1)
					if not obstacle.is_empty():
						clear=false;rejected.append([delay,d,str(obstacle[0].collider.get_parent().name)]);break
					if count>0 and absf(hit.position.y-last.y)>.225:
						clear=false;rejected.append([delay,d,"ledge"]);break
					last=hit.position;count+=1
				if clear:
					plan[key][end_name]={"begin":delay,"end":done,"checked":count}
					found=true;break
			if not found:failures.append([key,end_name])
			verification[key+"_"+end_name]=rejected
	var folder=OS.get_cmdline_user_args()[-1]
	FileAccess.open(folder+"/return_bake.json",FileAccess.WRITE).store_string(JSON.stringify({"tested":plan,"failures":failures,"rejected":verification},"  "))
	if failures.is_empty():FileAccess.open("res://assets/courtyard_r24/return_corridors.json",FileAccess.WRITE).store_string(JSON.stringify(plan,"  "))
	print("COURT14_RETURNS ",failures)
	quit(0 if failures.is_empty() else 3)

