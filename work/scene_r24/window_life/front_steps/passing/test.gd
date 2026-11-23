extends SceneTree

func _initialize()->void:
	call_deferred("check")

func check()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var block=game.street_block
	var people:Array=[]
	for t in block.tracks:
		if t.has("passing_offset"):people.append(t)
	var failed:Array=[]
	var tested: Array=[]
	var walker=game.explorer
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	for key in ["promenade","market_apron"]:
		var selected:Dictionary={}
		for t in people:
			if t.route!=key:continue
			var margin:float=minf(t.d,block.routes[key].get_baked_length()-t.d)
			if margin<6.5:continue
			var samples:Array=block.street_passing.surveyed[key]["forward" if t.sign>0 else "backward"]
			var cell:=int(t.d/block.routes[key].get_baked_length()*(samples.size()-1))
			if minf(samples[cell][0],samples[cell][1])>=.56:
				selected=t;break
		if selected.is_empty():
			failed.append("no passing site for "+key);continue
		var person:Node3D=selected.node
		var dir:float=selected.sign
		var start:Vector3=block.walk_position(key,selected.d+4.0*dir,dir)
		var goal:Vector3=block.walk_position(key,selected.d-4.2*dir,dir)
		var floor_hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP*.4,start-Vector3.UP*.6,1))
		if floor_hit.is_empty():failed.append(key+" floor");continue
		walker.begin_route_test(floor_hit.position+Vector3.UP*.035,goal)
		for i in 12:await physics_frame
		var nearest:=INF
		var furthest_side:=0.0
		var max_displacement:=0.0
		var max_ground_error:=0.0
		var previous:=person.global_position
		var arrived:=false
		for step in 660:
			walker.aim_route_test(goal)
			walker.automation_axis=Vector2(0,-.72)
			await physics_frame
			var foot:Vector3=walker.body.global_position
			var pos:=person.global_position
			nearest=minf(nearest,Vector2(foot.x-pos.x,foot.z-pos.z).length())
			furthest_side=maxf(furthest_side,absf(selected.passing_offset))
			max_displacement=maxf(max_displacement,pos.distance_to(previous));previous=pos
			var ground:=space.intersect_ray(PhysicsRayQueryParameters3D.create(pos+Vector3.UP*.20,pos-Vector3.UP*.25,1))
			if ground.is_empty():failed.append(key+" no resident foot support");break
			max_ground_error=maxf(max_ground_error,absf(pos.y-ground.position.y))
			if Vector2(foot.x-goal.x,foot.z-goal.z).length()<.25:
				arrived=true;break
		walker.end_route_test()
		for i in 130:await physics_frame
		var returned:bool=absf(selected.passing_offset)<.04
		var good:bool=arrived and nearest>=.55 and furthest_side>.18 and max_displacement<.24 and max_ground_error<.065 and returned
		var row={"route":key,"passed":good,"arrived":arrived,"closest_m":nearest,"shift_m":furthest_side,"max_resident_step_m":max_displacement,"foot_error_m":max_ground_error,"returned":returned}
		tested.append(row)
		if not good:failed.append(row)
	for t in people:
		if not t.node.get_node("WalkingResident").collision_layer==8:failed.append("resident volume")
	if not people.size()==9 or walker.walk_collision_mask!=13 or game.gameplay.scooter.collision_mask!=11:failed.append("collision layers")
	var report={"passed":failed.is_empty(),"failures":failed,"locals":people.size(),"encounters":tested}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	var outdir:String=preload("res://scripts/qa_context.gd").directory("res://verification_r24/build16/passing")
	DirAccess.make_dir_recursive_absolute(outdir)
	FileAccess.open(outdir+"/passing.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("STREET_PASSING ",report.passed," ",tested," ",failed)
	quit(0 if report.passed else 4)
