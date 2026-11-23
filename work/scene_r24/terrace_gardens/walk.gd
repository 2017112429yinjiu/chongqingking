extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay
	var actor=game.actor
	var route:=[Vector3(42.,9.64,75.),Vector3(46.8,10.21,72.),Vector3(48.2,10.74,68.),Vector3(52.9,11.45,65.2),Vector3(58.1,11.81,63.),Vector3(61.,12.30,61.5)]
	actor.begin_route_test(route.front()+Vector3.UP*.12,route[1]);await frames(40)
	actor.automation_driving=true
	var targets:=[];var samples:=[]
	game.owner_scene.hud.hide()
	for i in range(1,route.size()):
		var arrive:=false
		for tick in range(360):
			var foot:Vector3=actor.body.global_position
			var v:Vector3=route[i]-foot;v.y=0.
			if v.length()<.30:arrive=true;break
			actor.aim_route_test(foot+v.normalized()*5.+Vector3.UP*1.2)
			var ahead:Vector3=-actor.camera.global_basis.z;ahead.y=0;ahead=ahead.normalized()
			var right:=ahead.cross(Vector3.UP)
			actor.automation_axis=Vector2(v.dot(right),-v.dot(ahead)).normalized()
			if tick%6==0:samples.append([foot.x,foot.y,foot.z])
			if tick==12:await capture("passing_%02d"%i)
			await physics_frame
		targets.append(arrive)
		if not arrive:break
	actor.automation_axis=Vector2.ZERO
	check("walk_up_from_fork_past_the_car_and_planting",targets.size()==route.size()-1 and not false in targets,targets)
	FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE).store_string(JSON.stringify({"targets":targets,"path":samples,"checks":checks}))
	quit(2 if ever_failed else 0)
