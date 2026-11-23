extends SceneTree

func _initialize()->void:call_deferred("check")

func point(site:Dictionary,x:float,y:float)->Vector3:
	return Vector3(site.centre[0]+x,site.centre[1]+site.slope[0]*x+site.slope[1]*y,site.centre[2]-y)

func down(space:PhysicsDirectSpaceState3D,at:Vector3,mask:int)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.15,at-Vector3.UP*.17,mask))

func check()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var city:Node3D=game.get_node("City")
	var space:=city.get_world_3d().direct_space_state
	for name_key in ["COL_Terrain_200m_pavement","COL_East17_IronGrate"]:
		var body:=city.find_child(name_key,true,false).get_node("CQ_StaticCollision") as StaticBody3D
		body.collision_layer|=32 if name_key=="COL_Terrain_200m_pavement" else 64
	for key in ["East17_GullyBed","East17_GrateBearers"]:
		var obj:=city.find_child(key,true,false) as MeshInstance3D
		var support:=StaticBody3D.new()
		support.collision_layer=128 if key=="East17_GullyBed" else 256
		support.collision_mask=0
		var shape:=CollisionShape3D.new()
		shape.shape=obj.mesh.create_trimesh_shape()
		support.add_child(shape)
		obj.add_child(support)
	await physics_frame
	var sites:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/lane_inlets_r24/inlets.json"))
	var details:Array=[]
	var failures:Array=[]
	for site in sites:
		var metal:=0;var slots:=0;var supports:=0;var perimeter:=0
		var level:=0.;var bed_error:=0.;var outer_error:=0.
		for i in 15:
			var x:float=-.180+float(i)*.0257
			for y in [-.108,.0,.103]:
				var at:=point(site,x,y)
				var grate:=down(space,at,64)
				if i%2==0:
					if not grate.is_empty():
						metal+=1;level=maxf(level,absf(grate.position.y-at.y))
				else:
					var bed:=down(space,at,128)
					if grate.is_empty() and down(space,at,32).is_empty() and not bed.is_empty():
						slots+=1;bed_error=maxf(bed_error,absf((at.y-bed.position.y)-.055))
			if i%2!=0:
				for y in [-.079,.071]:
					var at:=point(site,x,y)
					var brace:=down(space,at,256)
					if not brace.is_empty() and absf(at.y-brace.position.y-.027)<.003:supports+=1
		for i in 10:
			var t:float=(i+.5)/10.
			for pair in [Vector2(-.244,-.15+t*.30),Vector2(.244,-.15+t*.30),Vector2(-.23+t*.46,-.164),Vector2(-.23+t*.46,.164)]:
				var at:=point(site,pair.x,pair.y)
				var hit:=down(space,at,32)
				if hit.is_empty():continue
				perimeter+=1;outer_error=maxf(outer_error,absf(hit.position.y-at.y))
		var clearance:=[]
		var capsule:=CapsuleShape3D.new()
		capsule.radius=.32;capsule.height=1.45
		var query:=PhysicsShapeQueryParameters3D.new()
		query.shape=capsule;query.collision_mask=1
		var axis:=Vector2.ZERO
		for deg in [48.,90.,0.,-40.,65.,-65.,22.,-20.]:
			var unit:=Vector2(cos(deg_to_rad(deg)),sin(deg_to_rad(deg)))
			var block:=[]
			for sample in range(-5,6):
				var offset:Vector2=unit*float(sample)*.20
				var at:=point(site,offset.x,offset.y)
				var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.45,at-Vector3.UP*.55,1))
				if h.is_empty() and absf(offset.x)<.235 and absf(offset.y)<.155:
					# The point can be inside an open slot while the character's sole spans two bars.
					var bar_index:=clampi(roundi((offset.x+.18)/.0514),0,7)
					var bar_at:=point(site,-.18+bar_index*.0514,offset.y)
					h=down(space,bar_at,64)
				if h.is_empty():block.append("missing floor");continue
				query.transform=Transform3D(Basis.IDENTITY,Vector3(at.x,h.position.y+.95,at.z))
				var hit:=space.intersect_shape(query,2)
				for obstacle in hit:block.append(str(obstacle.collider.get_parent().name))
			clearance.append([deg,block])
			if axis==Vector2.ZERO and block.is_empty():axis=unit
		var start:=point(site,-axis.x,-axis.y)
		var goal:=point(site,axis.x,axis.y)
		var floor_hit:=down(space,start,1)
		var walked:=0;var maximum:=0.;var total:=0.
		if axis!=Vector2.ZERO and not floor_hit.is_empty():
			var walker=game.explorer
			walker.begin_route_test(floor_hit.position+Vector3.UP*.035,goal)
			for tick in 12:await physics_frame
			var last:Vector3=walker.body.global_position
			for target in [goal,start]:
				walker.automation_axis=Vector2(0,-.68)
				var reached:=false
				for tick in 190:
					walker.aim_route_test(target);await physics_frame
					var now:Vector3=walker.body.global_position
					maximum=maxf(maximum,last.distance_to(now));total+=Vector2(now.x-last.x,now.z-last.z).length()
					last=now
					if Vector2(now.x-target.x,now.z-target.z).length()<.10:reached=true;break
				if reached:walked+=1
			walker.end_route_test()
		var ok:=metal==24 and slots==21 and supports==14 and perimeter==40 and level<.005 and bed_error<.003 and outer_error<.004 and walked==2 and maximum<.14
		details.append({"centre":site.centre,"metal":metal,"slots":slots,"bearers":supports,"outer_paving":perimeter,"bar_height_error_m":level,"bed_error_m":bed_error,"outer_error_m":outer_error,"walked":walked,"walk_m":total,"max_step_m":maximum,"approach_clearance":clearance,"axis":[axis.x,axis.y],"passed":ok})
		if not ok:failures.append(site.centre)
	var qa=preload("res://scripts/qa_context.gd")
	var report={"passed":sites.size()==2 and failures.is_empty(),"sites":details}
	qa.decorate(report,game)
	var dir:String=qa.directory("res://verification_r24/build17b")
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/inlets.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("EAST17B_TEST ",report.passed," ",details)
	quit(0 if report.passed else 4)
