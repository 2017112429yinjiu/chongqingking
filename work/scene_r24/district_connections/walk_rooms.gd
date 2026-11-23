extends SceneTree
func _initialize()->void:call_deferred("take")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func take()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	game.hud.hide()
	var args:=OS.get_cmdline_user_args()
	var folder:String=args[-1]
	DirAccess.make_dir_recursive_absolute(folder)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/connections_r24/layout.json"))
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	var walker=game.explorer
	var report:={"takes":[],"passed":true};var frame_id:=0
	for room:Dictionary in plan.rooms:
		if not room.id in ["A01_edge2_door","A04_edge3_window238637057"]:continue
		var shop:bool=room.id.ends_with("_door")
		var base:=v(room.front);var inward:=v(room.inward);var side:=inward.cross(Vector3.UP)
		var start:=base+side*(.12 if shop else -1.45)-inward*(1.20 if shop else 2.75)
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start+Vector3.UP*1.35,start-Vector3.UP*3.3,1))
		if hit.is_empty():report.passed=false;continue
		var grades:=[]
		for ix in 28:
			var sample:=base+side*.12+inward*(-1.40+ix*.075) if shop else base-inward*2.75+side*(-1.50+ix*.12)
			var floor_sample:=space.intersect_ray(PhysicsRayQueryParameters3D.create(sample+Vector3.UP*.83,sample-Vector3.UP*1.6,1))
			if not floor_sample.is_empty():grades.append([ix,floor_sample.position.y,str(floor_sample.collider.get_parent().name)])
		var goals:Array=[base+side*.13+inward*.55,base+side*.12+inward*2.58,base+inward*(room.new_depth-1.18)] if shop else [base+side*.20-inward*2.75,base+side*1.45-inward*2.75]
		var focus:Vector3=base+inward*(room.new_depth-.40)+Vector3.UP*1.43
		walker.begin_route_test(hit.position+Vector3.UP*.035,focus)
		for i in 12:await physics_frame
		var from:Vector3=walker.body.global_position;var prev:=from;var travel:=0.;var largest:=0.;var reached:=0;var timeline:=[];var tick:=0
		for goal:Vector3 in goals:
			var arrived:=false
			for i in 340:
				var pos:Vector3=walker.body.global_position
				if shop and reached>0:focus=focus.lerp(base+side*.45+inward*(room.new_depth-.15)+Vector3.UP*1.18,.045)
				walker.camera.look_at(focus,Vector3.UP);walker._sync_angles()
				var ahead:Vector3=-walker.camera.global_basis.z;ahead.y=0.;ahead=ahead.normalized()
				var delta:=goal-pos;delta.y=0.
				if delta.length()<.13:arrived=true;break
				var direction:=delta.normalized()
				walker.automation_axis=Vector2(direction.dot(ahead.cross(Vector3.UP)),-direction.dot(ahead))*.58
				await physics_frame
				var now:Vector3=walker.body.global_position
				largest=maxf(largest,now.distance_to(prev));travel+=Vector2(now.x-prev.x,now.z-prev.z).length();prev=now
				if tick%5==0 and not "--no-images" in args:
					await RenderingServer.frame_post_draw
					var pic:=root.get_texture().get_image()
					if pic.is_empty() or pic.save_jpg(folder.path_join("frame_%03d.jpg"%frame_id),.92)!=OK:quit(3);return
					timeline.append([frame_id,tick,now.x,now.y,now.z]);frame_id+=1
				tick+=1
			if arrived:reached+=1
			else:break
		walker.end_route_test()
		var ok:=reached==goals.size() and largest<.27
		report.takes.append({"id":room.id,"goals":reached,"expected":goals.size(),"passed":ok,"grades":grades,"walk_m":travel,"max_step_m":largest,"depth_reached_m":(prev-base).dot(inward),"start":[from.x,from.y,from.z],"stop":[prev.x,prev.y,prev.z],"frames":timeline})
		if not ok:report.passed=false
	preload("res://scripts/qa_context.gd").decorate(report,game)
	FileAccess.open(folder.path_join("rooms_walk.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("ROOM18_WALK ",report.passed," ",frame_id)
	quit(0 if report.passed else 4)
