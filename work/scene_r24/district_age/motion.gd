extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(8)
	game=scene.gameplay
	var actor=game.actor
	var start:=Vector3(-71.8,15.75,28.15)
	var goal:=Vector3(-69.9,15.62,18.7)
	actor.begin_route_test(start,goal);await frames(40)
	actor.automation_driving=true
	var points:=[]
	for tick in range(420):
		var foot:Vector3=actor.body.global_position
		var direction:=Vector2(goal.x-foot.x,goal.z-foot.z)
		if direction.length()<.27:break
		# Look to the side at the shelter while walking up the lane. Drive local axes through the real walking controller.
		actor.aim_route_test(Vector3(-66.5,foot.y+1.12,22.65))
		var ahead:Vector3=-actor.camera.global_basis.z;ahead.y=0;ahead=ahead.normalized()
		var right:=ahead.cross(Vector3.UP)
		var v:=Vector3(direction.x,0,direction.y).normalized()
		actor.automation_axis=Vector2(v.dot(right),-v.dot(ahead)).normalized()
		if tick%10==0:
			points.append([foot.x,foot.y,foot.z]);await capture("walk_%03d"%tick)
		await physics_frame
	actor.automation_axis=Vector2.ZERO
	var end:Vector3=actor.body.global_position
	check("passed_shelter_on_foot",Vector2(end.x-goal.x,end.z-goal.z).length()<.45 and end.distance_to(start)>8.,str(end))
	FileAccess.open(output.path_join("motion.json"),FileAccess.WRITE).store_string(JSON.stringify({"points":points,"checks":checks}))
	quit(2 if ever_failed else 0)
