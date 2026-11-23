extends SceneTree
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func shot(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,mask:int)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b,mask))
func floor_hit(space:PhysicsDirectSpaceState3D,at:Vector3,mask:int)->Dictionary:
	return shot(space,at+Vector3.UP*.50,at-Vector3.UP*.90,mask)
func walk(walker:Node,space:PhysicsDirectSpaceState3D,points:Array)->Dictionary:
	var path:=points.duplicate()
	var reversed:=points.duplicate()
	reversed.reverse()
	path.append_array(reversed.slice(1))
	var foot:=floor_hit(space,path[0],1)
	if foot.is_empty():return {"passed":false,"error":"missing start"}
	walker.begin_route_test(foot.position+Vector3.UP*.035,path[1])
	for i in 16:await physics_frame
	var previous:Vector3=walker.body.global_position
	var total:=0.;var largest:=0.;var goals:=0
	for goal:Vector3 in path.slice(1):
		walker.automation_axis=Vector2(0,-.77)
		var reached:=false
		for tick in 300:
			walker.aim_route_test(goal);await physics_frame
			var p:Vector3=walker.body.global_position
			total+=Vector2(p.x-previous.x,p.z-previous.z).length()
			largest=maxf(largest,p.distance_to(previous));previous=p
			if Vector2(p.x-goal.x,p.z-goal.z).length()<.21:reached=true;break
		if not reached:break
		goals+=1
	walker.end_route_test()
	return {"passed":goals==path.size()-1 and largest<.27,"goals":goals,"expected":path.size()-1,"metres":total,"max_step_m":largest,"stop":[previous.x,previous.y,previous.z]}
func run()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/connections_r24/layout.json"))
	var city:Node3D=game.get_node("City")
	var space:=city.get_world_3d().direct_space_state
	var failures:=[]
	for spec in [["COL_D18_StoneFlights",16],["COL_D18_LaneShoulders",32],["COL_D18_NanquShoulder",64],["COL_D18_RoomShells",128]]:
		var obj:=city.find_child(spec[0],true,false)
		if obj==null:push_error(str(spec));quit(3);return
		obj.get_node("CQ_StaticCollision").collision_layer|=spec[1]
	await physics_frame
	var stairs:Dictionary={};var checks:=0;var anomalies:=[];var gaps:=[]
	for row in plan.stairs:
		var mid:=v(row.point)
		var n:=Vector3(row.normal_xy[0],0,-row.normal_xy[1])
		if not stairs.has(row.lane):stairs[row.lane]=[]
		stairs[row.lane].append(mid)
		for frac in [-.85,-.42,0,.42,.85]:
			var at:Vector3=mid+n*float(frac)*float(row.width)*.5
			var exact:=floor_hit(space,at,16)
			var public_floor:=floor_hit(space,at,1)
			checks+=1
			if exact.is_empty() or public_floor.is_empty() or absf(exact.position.y-mid.y)>.005 or absf(public_floor.position.y-mid.y)>.035:
				anomalies.append([row.lane,row.row,frac,str(public_floor.collider.get_parent().name) if not public_floor.is_empty() else "",public_floor.position.y-mid.y if not public_floor.is_empty() else null])
		for side in [-1,1]:
			for offset in [.08,.34,.66]:
				var at:=mid+n*float(side)*(float(row.width)*.5+float(offset))
				if floor_hit(space,at,32).is_empty():gaps.append([row.lane,row.row,side,offset])
	var road_checks:=0;var road_errors:=[]
	var path:=[]
	for i in plan.banks.size():
		var section:Array=plan.banks[i]
		for k in section.size()-1:
			var at:=v(section[k]).lerp(v(section[k+1]),.5)
			if i==0:continue
			at=v(plan.banks[i-1][k]).lerp(v(plan.banks[i][k+1]),.5)
			var base:=floor_hit(space,at,64)
			var all:=floor_hit(space,at,1)
			road_checks+=1
			if base.is_empty() or all.is_empty() or absf(at.y-base.position.y)>.045 or absf(base.position.y-all.position.y)>.045:road_errors.append([i,k,at.y,base.get("position"),str(all.collider.get_parent().name) if not all.is_empty() else ""])
		if i%8==1:path.append(v(section[1]))
	# Camera rays through the actual player's white wedge. These failed in the third candidate.
	var sight: Array=[]
	var view:Dictionary=game.art_profile.diagnostic_views.r24_join18_road
	var eye:=v(view.position)
	var forward:=eye.direction_to(v(view.target))
	var camera_right:=forward.cross(Vector3.UP).normalized()
	var up:=camera_right.cross(forward)
	for pixel:Vector2 in [Vector2(424,253),Vector2(428,252),Vector2(420,256),Vector2(439,249),Vector2(424,251)]:
		var ray:Vector3=(forward+(camera_right*((pixel.x+.5-480.)/270.)+up*((270.-pixel.y-.5)/270.))*tan(deg_to_rad(float(view.fov)*.5))).normalized()
		var h:=shot(space,eye,eye+ray*46.,64)
		var distance:float=h.position.distance_to(eye) if not h.is_empty() else -1.
		sight.append([pixel.x,pixel.y,distance])
		if distance<12. or distance>39.:failures.append("road oblique pixel "+str(pixel))
	var walks:={}
	for key in stairs:walks[key]=await walk(game.explorer,space,stairs[key])
	walks["road"]=await walk(game.explorer,space,path)
	var rooms:=[]
	for room in plan.rooms:
		var f:=v(room.front);var inward:=v(room.inward);var right:=inward.cross(Vector3.UP)
		var hits:=[]
		for lateral in [-.31,0.,.31]:
			var a:Vector3=f+right*float(lateral)+Vector3.UP*1.45+inward*.34
			var stop:=shot(space,a,a+inward*8,128)
			var public_hit:=shot(space,a,a+inward*8,1)
			var d:float=(stop.position-f).dot(inward) if not stop.is_empty() else -1
			var used:float=(public_hit.position-f).dot(inward) if not public_hit.is_empty() else -1
			hits.append([d,used,str(public_hit.collider.get_parent().name) if not public_hit.is_empty() else ""])
			if d<room.new_depth-.12 or used<room.new_depth-.17:failures.append("room "+room.id);break
		rooms.append([room.id,hits])
	if not anomalies.is_empty():failures.append("tread surface")
	if not gaps.is_empty():failures.append("open shoulders")
	if not road_errors.is_empty():failures.append("road surface")
	for key in walks:
		if not walks[key].passed:failures.append("walk "+key)
	var installed:Dictionary=game.scene_identity.get("district_connections",{})
	if not installed.get("missing",["all"]).is_empty():failures.append("missing meshes")
	var report:={"passed":failures.is_empty(),"failures":failures,"tread_probes":checks,"tread_errors":anomalies,"shoulder_probes":plan.stairs.size()*6,"shoulder_errors":gaps,"road_probes":road_checks,"road_errors":road_errors,"road_sightlines":sight,"rooms":rooms,"walks":walks}
	var qa=preload("res://scripts/qa_context.gd");qa.decorate(report,game)
	var dir:String=qa.directory("res://verification_r24/build18");DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/connections.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("JOINTS18 ",report.passed," ",failures," ",anomalies.size()," ",gaps.size()," ",road_errors.size()," ",installed)
	quit(0 if report.passed else 4)
