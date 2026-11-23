extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	game=scene.gameplay;bike=game.scooter
	bike.enter(game.actor);bike.automation=true
	var space:=scene.get_world_3d().direct_space_state
	var along:=Vector2(.8258,.4863).normalized()
	var across:=Vector2(along.y,-along.x)
	var origin:=Vector2(-29.669,-86.431)
	var rows:=[]
	for station:float in [8.,10.5,13.]:
		for reverse:bool in [false,true]:
			var edge:=origin+along*station
			var a:=edge+across*(.88 if reverse else -2.40)
			var b:=edge+across*(-2.40 if reverse else .88)
			var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(a.x,35.,a.y),Vector3(a.x,29.,a.y),1))
			if hit.is_empty():check("north_start_supported",false);continue
			var d:=(b-a).normalized()
			bike.global_position=hit.position+Vector3.UP*.13
			bike.rotation=Vector3(0,atan2(-d.x,-d.y),0)
			bike.velocity=Vector3.ZERO;bike.speed=0.;bike.parked=false;bike.last_obstacle={};bike.test_throttle=0.;bike.test_steer=0.;bike.test_brake=true
			await frames(22)
			bike.test_brake=false
			var reached:=false
			for tick in range(260):
				bike.test_throttle=1. if bike.speed<2.3 else 0.
				await physics_frame
				if (Vector2(bike.global_position.x,bike.global_position.z)-a).dot(d)>a.distance_to(b)-.14:reached=true;break
			rows.append({"station":station,"reverse":reverse,"passed":reached,"end":str(bike.global_position),"contact":bike.last_obstacle.duplicate(true)})
			check("north_road_ramp_"+str(station)+"_"+str(reverse),reached,bike.global_position)
	FileAccess.open(output.path_join("rides.json"),FileAccess.WRITE).store_string(JSON.stringify(rows))
	quit(2 if ever_failed else 0)
