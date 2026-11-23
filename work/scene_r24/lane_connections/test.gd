extends SceneTree

const PLAN := "res://assets/lane_connection_r24/layout.json"
func _initialize()->void:call_deferred("test")

func top(space:PhysicsDirectSpaceState3D, p:Vector3, mask:int, above:=.27, below:=.34)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*above,p-Vector3.UP*below,mask))

func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])

func test()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var failed:Array=[]
	var city:Node3D=game.get_node("City")
	var space:=city.get_world_3d().direct_space_state
	var masks:Dictionary={"COL_East17_TerraceSteps":16,"COL_Walk_Upper_courtyard_walk_pavement":32,"COL_East17_IronGrate":64}
	for key in masks:
		var body:=city.find_child(key,true,false).get_node("CQ_StaticCollision") as StaticBody3D
		body.collision_layer|=masks[key]
	await physics_frame
	var floor_errors:Array=[]
	var max_height:=0.0
	for target in plan.floor_probes:
		var point:=Vector3(target[0],target[1],target[2])
		var native:=top(space,point,16 if target[3]=="stair" else 32)
		var all_hits:=top(space,point,1)
		var error:float=999 if native.is_empty() else absf(native.position.y-point.y)
		max_height=maxf(error,max_height)
		if error>.003 or all_hits.is_empty() or absf(all_hits.position.y-point.y)>.020:
			floor_errors.append([target,error,str(all_hits.collider.get_parent().name) if not all_hits.is_empty() else "",all_hits.position.y-point.y if not all_hits.is_empty() else null])
	if not floor_errors.is_empty():failed.append("tread_or_landing_height")
	var join_count:=0
	var join_errors:Array=[]
	for i in plan.join.size()-1:
		var a:=v(plan.join[i])
		var b:=v(plan.join[i+1])
		for fraction in [.12,.5,.88]:
			var midpoint:=a.lerp(b,fraction)
			for across in [-.018,.018]:
				var at:=midpoint+Vector3.RIGHT*float(across)
				var hit:=top(space,at,32 if across<0 else 16)
				var extra:=top(space,at,16 if across<0 else 32)
				if hit.is_empty() or absf(hit.position.y-at.y)>.002 or not extra.is_empty():
					join_errors.append([i,fraction,across])
				join_count+=1
	if not join_errors.is_empty():failed.append("shared_edge")
	var ring:Array=plan.drain_rim
	var metal_checks:=0
	var clear_slots:=0
	var drain_error:=0.
	var grate_fail:Array=[]
	for j in 15:
		var u:float=(.235-.180+float(j)*.0257)/.47
		for t in [.14,.48,.85]:
			var front:=v(ring[0]).lerp(v(ring[1]),u)
			var back:=v(ring[3]).lerp(v(ring[2]),u)
			var at:=front.lerp(back,t)
			var metal:=top(space,at,64,.075,.085)
			var old_floor:=top(space,at,32,.075,.085)
			if j%2==0:
				if metal.is_empty():grate_fail.append([j,t,"missing rail"])
				else:drain_error=maxf(drain_error,absf(metal.position.y-at.y));metal_checks+=1
			else:
				if metal.is_empty() and old_floor.is_empty():clear_slots+=1
				else:grate_fail.append([j,t,"blocked slot"])
	if drain_error>.006 or not grate_fail.is_empty():failed.append("grate_seat")
	var bed:=city.find_child("East17_GullyBed",true,false) as MeshInstance3D
	var bed_probe:=StaticBody3D.new()
	bed_probe.collision_layer=128
	bed_probe.collision_mask=0
	var bed_shape:=CollisionShape3D.new()
	bed_shape.shape=bed.mesh.create_trimesh_shape()
	bed_probe.add_child(bed_shape)
	bed.add_child(bed_probe)
	await physics_frame
	var depth_errors:Array=[]
	var depths:Array=[]
	for j in 7:
		var fraction:float=(.235-.180+(2*j+1)*.0257)/.47
		var at:=v(ring[0]).lerp(v(ring[1]),fraction).lerp(v(ring[3]).lerp(v(ring[2]),fraction),.50)
		var hit:=top(space,at,128,.075,.105)
		if hit.is_empty():depth_errors.append(j);continue
		var depth:float=at.y-hit.position.y
		depths.append(depth)
		if absf(depth-.055)>.003:depth_errors.append(j)
	if not depth_errors.is_empty():failed.append("gully_bed")
	var eye:=Vector3(26.799273,24.566343,-6.865393)
	var look:=(Vector3(28.469639,22.931823,-11.285599)-eye).normalized()
	var right:=look.cross(Vector3.UP).normalized()
	var up:=right.cross(look)
	var oblique:Array=[]
	var leak_count:=0
	for pixel in [Vector2(676,261),Vector2(682,263),Vector2(757,280)]:
		for dx in [-1,0,1]:
			for dy in [-1,0,1]:
				var dir:Vector3=(look+(right*((pixel.x+dx+.5-599.)/360.)+up*((360.-pixel.y-dy-.5)/360.))*tan(deg_to_rad(70.116399)*.5)).normalized()
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(eye,eye+dir*19.,1))
				if hit.is_empty():leak_count+=1
				oblique.append([pixel.x+dx,pixel.y+dy,str(hit.collider.get_parent().name) if not hit.is_empty() else "",eye.distance_to(hit.position) if not hit.is_empty() else null])
	if leak_count:failed.append("oblique_leak")
	var coverage:=0
	var gaps:Array=[]
	var grate_center:=v(plan.drain_center)
	for ix in 57:
		for iz in 64:
			var at:=Vector3(24.35+(ix+.5)*12.1/57.,24.,-(6.45+(iz+.5)*13.40/64.))
			if Vector2(at.x-grate_center.x,at.z-grate_center.z).length()<.30:continue
			coverage+=1
			if top(space,at,1,3.,4.).is_empty():gaps.append([at.x,at.z])
	if not gaps.is_empty():failed.append("open_ground")
	var walker=game.explorer
	var routes=[]
	var branch:Array[Vector3]=[Vector3(33.55,22.4,-7.0)]
	for row in plan.steps:
		var mid:=Vector3.ZERO
		for pt in row: mid+=Vector3(pt[0],0,-pt[1])*.25
		branch.append(mid)
	branch.append(Vector3(28.05,23.5,-13.8));branch.append(Vector3(28.63,23.8,-16.6))
	var highway:Array[Vector3]=[Vector3(26.68,22.6,-8.1),Vector3(27.44,23.,-11.22),Vector3(28.0,23.5,-13.72),Vector3(28.42,23.8,-16.1),Vector3(29.15,24.3,-18.96)]
	for path in [highway,branch]:
		var first:Vector3=path[0]
		var foot:=top(space,first,1,1.2,1.4)
		if foot.is_empty():failed.append("start");continue
		walker.begin_route_test(foot.position+Vector3.UP*.035,path[1])
		for i in 15:await physics_frame
		var goals:Array=path.slice(1);var reverse:Array=path.duplicate();reverse.reverse();goals.append_array(reverse.slice(1))
		var last:Vector3=walker.body.global_position
		var total:=0.;var max_step:=0.;var reached:=0
		for goal:Vector3 in goals:
			walker.automation_axis=Vector2(0,-.79)
			var ok:=false
			for tick in 440:
				walker.aim_route_test(goal);await physics_frame
				var now:Vector3=walker.body.global_position
				total+=Vector2(now.x-last.x,now.z-last.z).length();max_step=maxf(max_step,now.distance_to(last));last=now
				if Vector2(now.x-goal.x,now.z-goal.z).length()<.21:ok=true;break
			if ok:reached+=1
			else:break
		walker.end_route_test()
		routes.append({"goals":reached,"expected":goals.size(),"metres":total,"max_step":max_step,"end":[last.x,last.y,last.z]})
		if reached!=goals.size() or max_step>.27:failed.append("walk")
	var installed:Dictionary=game.scene_identity.get("east_lane_joint",{})
	if installed.get("replaced",0)!=plan.source_nodes.size() or not installed.get("missing",["unknown"]).is_empty():failed.append("install")
	var report={"passed":failed.is_empty(),"failures":failed,"floors":plan.floor_probes.size(),"floors_failed":floor_errors,"max_floor_m":max_height,"edge_samples":join_count,"edge_failed":join_errors,"grate_bars":metal_checks,"clear_slots":clear_slots,"grate_failed":grate_fail,"grate_error_m":drain_error,"walks":routes}
	var qa=preload("res://scripts/qa_context.gd")
	report.merge({"gully_depths_m":depths,"bed_errors":depth_errors,"oblique":oblique,"oblique_misses":leak_count,"courtyard_probes":coverage,"open_ground":gaps})
	qa.decorate(report,game)
	var dir:String=qa.directory("res://verification_r24/build17")
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/junction.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("JUNCTION17 ",report.passed," ",failed," ",floor_errors.size()," ",join_errors.size()," ",grate_fail.size()," ",routes)
	quit(0 if report.passed else 3)
