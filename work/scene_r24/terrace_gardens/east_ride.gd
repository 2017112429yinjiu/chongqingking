extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	game=scene.gameplay;bike=game.scooter
	bike.enter(game.actor);bike.automation=true
	var report:=[]
	for x:float in [35.25,35.63,36.12]:
		for reverse:bool in [false,true]:
			var start:=Vector3(x,22.46,-5.02) if reverse else Vector3(x,21.88,-1.95)
			var goal:=-1.95 if reverse else -5.02
			bike.global_position=start+Vector3.UP*.13;bike.rotation=Vector3(0,PI if reverse else 0.,0)
			bike.velocity=Vector3.ZERO;bike.speed=0.;bike.parked=false;bike.last_obstacle={};bike.test_throttle=0.;bike.test_steer=0.;bike.test_brake=true
			await frames(22)
			bike.test_brake=false
			var reached:=false
			for tick in range(250):
				bike.test_throttle=1. if bike.speed<2.1 else 0.
				await physics_frame
				if (reverse and bike.global_position.z>=goal) or (not reverse and bike.global_position.z<=goal):reached=true;break
			report.append({"x":x,"reverse":reverse,"passed":reached,"end":str(bike.global_position),"last_contact":bike.last_obstacle.duplicate(true)})
			check("east_landing_"+str(x)+"_"+str(reverse),reached,bike.global_position)
	FileAccess.open(output.path_join("rides.json"),FileAccess.WRITE).store_string(JSON.stringify(report))
	quit(2 if ever_failed else 0)
