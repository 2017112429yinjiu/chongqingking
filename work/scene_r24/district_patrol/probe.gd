extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	await frames(20)
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	for i in 26:
		var x:float=-61.6+i*.24
		var y:float=19.89+clampf((x+60.98)/4.76,0.,1.)*3.01
		for h:float in [.25,1.1,1.71]:
			var p:=Vector3(x,y+h,17.52)
			var q:=PhysicsRayQueryParameters3D.create(p,p+Vector3.RIGHT*.38,1)
			q.hit_back_faces=true
			var hit:=space.intersect_ray(q)
			if hit:print("PROBE ",p," ",hit.position," ",hit.collider.get_parent().name)
		var foot:=Vector3(x,y+.32,17.52)
		var q:=PhysicsRayQueryParameters3D.create(foot,foot+Vector3.UP*3.,1)
		q.hit_back_faces=true
		var hit:=space.intersect_ray(q)
		if hit:print("HEAD ",x," ",hit.position.y-y," ",hit.collider.get_parent().name)
	quit()
