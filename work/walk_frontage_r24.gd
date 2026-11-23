extends SceneTree

func _initialize() -> void:
	call_deferred("walk")

func walk() -> void:
	var world := load("res://main.tscn").instantiate() as Node3D
	root.add_child(world)
	while world.gameplay==null or world.street_block.tracks.is_empty():await physics_frame
	var directory: String=preload("res://scripts/qa_context.gd").directory("res://verification_r24/walk")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var walker: Node3D=world.explorer
	var curve: Curve3D=world.street_block.routes.promenade
	var trail: Array[Vector3]=[]
	for east in [-46.,-41.,-36.,-31.,-26.,-22.]:
		var closest:=Vector3.ZERO
		var error:=100.
		for point in curve.get_baked_points():
			if absf(point.x-east)<error:
				error=absf(point.x-east);closest=point
		trail.append(closest)
	trail.append(Vector3(-21.4,9.5,77.1))
	trail.append(Vector3(-21.4,9.8,75.4))
	trail.append(Vector3(-25.8,9.7,75.6))
	for point in [Vector3(-21.0,9.4,76.7),Vector3(-16.4,9.7,76.4),Vector3(-13.1,9.8,75.4),Vector3(-18.8,9.6,76.7),Vector3(-21.35,9.5,77.27),Vector3(-21.4,8.2,80.85),Vector3(-24.6,8.1,81.15)]:
		trail.append(point)
	world.hud.hide()
	walker.begin_route_test(trail[0]+Vector3.UP*.035,trail[1])
	for frame in 20:await physics_frame
	var previous: Vector3=walker.body.global_position
	var total:=0.;var max_step:=0.;var rows: Array=[];var stalls: Array=[];var views: Array=[]
	walker.automation_axis=Vector2(0,-1)
	for idx in range(1,trail.size()):
		var reached:=false
		for frame in 350:
			walker.aim_route_test(trail[idx]);await physics_frame
			var pos: Vector3=walker.body.global_position
			total+=Vector2(pos.x-previous.x,pos.z-previous.z).length()
			max_step=maxf(max_step,pos.distance_to(previous));previous=pos
			if Vector2(pos.x-trail[idx].x,pos.z-trail[idx].z).length()<.25:
				reached=true;break
		rows.append({"waypoint":idx,"arrived":reached,"position":[previous.x,previous.y,previous.z]})
		if not reached:
			for k in walker.body.get_slide_collision_count():
				stalls.append(str(walker.body.get_slide_collision(k).get_collider().get_parent().name))
			break
		if DisplayServer.get_name()!="headless" and idx in [2,5,6,8,11,14,15]:
			walker.automation_axis=Vector2.ZERO
			if idx in [8,11]:
				var sight:=Vector3(-26.12,10.49,74.12) if idx==8 else Vector3(-12.39,10.61,72.23)
				var camera: Camera3D=walker.camera
				var begin:=camera.global_basis
				var finish:=Basis.looking_at((sight-camera.global_position).normalized(),Vector3.UP)
				for step in 28:
					camera.global_basis=begin.slerp(finish,smoothstep(0.,1.,(step+1.)/28.))
					walker._sync_angles()
					await physics_frame
				for frame in 5:
					camera.look_at(sight,Vector3.UP)
					walker._sync_angles()
					await RenderingServer.frame_post_draw
				views.append({"waypoint":idx,"eye":str(camera.global_position),"aim_alignment":-camera.global_basis.z.dot((sight-camera.global_position).normalized())})
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(directory+"/walking_%02d.png"%idx)
			walker.automation_axis=Vector2(0,-1)
	walker.end_route_test()
	var report:={"success":rows.size()==trail.size()-1 and rows.back().arrived and max_step<.8,"metres":total,"max_frame_m":max_step,"waypoints":rows,"stall_colliders":stalls}
	report.looks=views
	for view in views:report.success=report.success and view.aim_alignment>.995
	var market=world.get_node_or_null("City/MarketTerraceR24")
	if market:
		var probe_ok:=true
		for item in market.manifest.fixtures:
			if item.kind!="counter":continue
			var origin:=Vector3(item.position[0],item.position[1]+item.size[1]*.35,item.position[2]+item.size[2]*.5+.25)
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,origin+Vector3.FORWARD*.42,1))
			probe_ok=probe_ok and not hit.is_empty() and str(hit.collider.name).begins_with("StallCounter")
		var bridge_checks:=0
		var soffit_checks:=0
		for x in range(-23,26):
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,13.,100.),Vector3(x,8.,100.),1))
			if not hit.is_empty() and hit.normal.y>.94 and hit.position.y>10.65 and hit.position.y<11.25:bridge_checks+=1
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,9.44,100.),Vector3(x,10.5,100.),1)
			var bottom:=world.get_world_3d().direct_space_state.intersect_ray(query)
			if not bottom.is_empty() and str(bottom.collider.get_parent().name).contains("FlyoverBox") and bottom.normal.y<-.94:soffit_checks+=1
		report.bridge_soffit_hits=soffit_checks
		report.success=report.success and soffit_checks>=44
		report.bridge_top_hits=bridge_checks
		report.success=report.success and bridge_checks==49
		report.counters_block=probe_ok
		report.success=report.success and probe_ok
		report.seller_greetings=market.greeting_count
		report.seller_feet=str(market.seller.position)
		report.success=report.success and market.greeting_count>=1 and market.result.missing.is_empty()
	preload("res://scripts/qa_context.gd").decorate(report,world)
	var file:=FileAccess.open(directory+"/walk.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	print("FRONTAGE_WALK ",report.success," ",total," ",stalls)
	quit(0 if report.success else 2)

