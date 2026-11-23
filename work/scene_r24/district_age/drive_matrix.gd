extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay;lesson=game.lesson;bike=game.scooter
	var query:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/road_queries.json"))
	var lines:={}
	for row:Array in query.sections:
		if row[1]!=1 or row[4]==null:continue
		var id:=int(row[0])
		var p:=Vector3(row[2],row[4],row[3])
		if absf(p.x)>98.5 or absf(p.z)>98.5:continue
		if not lines.has(id):lines[id]=[]
		var pts:Array=lines[id]
		if pts.is_empty() or Vector2(pts[-1].x-p.x,pts[-1].z-p.z).length()>1.60:pts.append(p)
	var batch_id:=0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--batch="):batch_id=int(arg.trim_prefix("--batch="))
	var results:=[]
	bike.enter(game.actor);bike.automation=true
	for id:int in lines:
		if id%3!=batch_id:continue
		var pts:Array=lines[id].duplicate()
		if "--reverse" in OS.get_cmdline_user_args():pts.reverse()
		if pts.size()<2:
			results.append({"id":id,"state":"outside_inner_test_area"});continue
		var d:Vector3=pts[1]-pts[0]
		# Only the initial spawn is placed. Every subsequent metre uses normal steering, throttle and collisions.
		bike.global_position=pts[0]+Vector3.UP*.19;bike.rotation=Vector3(0,atan2(-d.x,-d.z),0)
		bike.velocity=Vector3.ZERO;bike.speed=0.;bike.parked=false;bike.last_obstacle={};bike.test_throttle=0.;bike.test_brake=true
		await frames(22)
		var next:=1;var still:=0;var best:=INF;var history:Array=[];var tick:=0
		var start:Vector3=bike.global_position
		while tick<pts.size()*140+300 and next<pts.size() and still<210:
			var p:Vector3=bike.global_position
			var delta:Vector3=pts[next]-p;delta.y=0
			if delta.length()<.93:
				next+=1;still=0;best=INF;continue
			if delta.length()<best-.07:best=delta.length();still=0
			else:still+=1
			var steering:=(-bike.global_basis.z).signed_angle_to(delta.normalized(),Vector3.UP)
			bike.test_steer=clampf(steering*2.45,-1.,1.)
			var v:=2.0 if absf(steering)>.40 else 3.85
			bike.test_brake=bike.speed>v+.4
			bike.test_throttle=1. if bike.speed<v else 0.
			if tick%24==0:history.append([p.x,p.y,p.z,next])
			await physics_frame;tick+=1
		var pass_route:=next==pts.size()
		results.append({"id":id,"route":query.routes[id].name,"part":query.routes[id].part,"reached":next-1,"targets":pts.size()-1,"state":"passed" if pass_route else "stopped","start":str(start),"end":str(bike.global_position),"goal":str(pts[mini(next,pts.size()-1)]),"last_contact":bike.last_obstacle.duplicate(true),"history":history})
		print("ROUTE_MATRIX ",id," ",results[-1].state," ",next-1,"/",pts.size()-1)
		FileAccess.open(output.path_join("drives.json"),FileAccess.WRITE).store_string(JSON.stringify(results))
	quit()
