extends "../../continuous_site_walk.gd"

func station(plot: Dictionary, u: float, v: float) -> Dictionary:
	var r: float=plot.bearing
	var p: Array=plot.east_north
	var origin:=Vector3(p[0]+cos(r)*u-sin(r)*v,plot.height+1.75,-p[1]-sin(r)*u-cos(r)*v)
	var query:=PhysicsRayQueryParameters3D.create(origin,origin-Vector3.UP*9.,1)
	var hit:=scene.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty(): return {}
	return {"position":hit.position,"owner":str(hit.collider.get_parent().name)}

func walk_step(goals: Array, label: String) -> Array:
	var contacts: Array=[]
	var observe:=func() -> void:
		var body: CharacterBody3D=scene.explorer.body
		var active: Array=[]
		for i in body.get_slide_collision_count():
			var hit:=body.get_slide_collision(i)
			active.append({"mesh":str(hit.get_collider().get_parent().name),"point":enu(hit.get_position()),"normal":enu(hit.get_normal())})
		if Engine.get_physics_frames()%3==0 and not active.is_empty():
			contacts.append({"body":enu(body.global_position),"hits":active})
	physics_frame.connect(observe)
	await leg_without_placement(label,goals)
	physics_frame.disconnect(observe)
	return contacts

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	var geo: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var plot: Dictionary=geo.plots.filter(func(row: Dictionary) -> bool: return int(row.plot_id)==53)[0]
	var upper: float=plot.depth*.5
	var lower: float=upper+plot.back_stair_m
	var measured: Array=[]
	var route: Array=[]
	for offset: float in [.14,1.78,3.38,4.96,6.55,8.20,plot.back_stair_m+.60]:
		var hit:=station(plot,plot.door_u+.12,upper+offset)
		if hit.is_empty(): continue
		route.append(hit.position+Vector3.UP*.040)
		measured.append({"u":plot.door_u+.12,"v":upper+offset,"enu":enu(hit.position),"owner":hit.owner})
	if not check("all_original_stair_waypoints_supported",route.size()==7,measured):
		quit(2)
		return
	scene.explorer.begin_route_test(route[0],route[1])
	await frames(20)
	var start: Vector3=scene.explorer.body.global_position
	var down:=await walk_step(route.slice(1),"53_down_original_stairs")
	var low: Vector3=scene.explorer.body.global_position
	route.reverse()
	var up:=await walk_step(route.slice(1),"53_up_original_stairs")
	var finish: Vector3=scene.explorer.body.global_position
	check("same_upper_start_and_return",finish.distance_to(start)<.55,{"back_gap_m":finish.distance_to(start),"walked_vertical_m":start.y-low.y})
	for phase in [down,up]:
		check("recorded_tread_contacts",phase.any(func(row: Dictionary):return row.hits.any(func(h: Dictionary):return str(h.mesh).begins_with("COL_Outer500_Retaining_and_boundaries"))),phase.size())
	FileAccess.open(output.path_join("stairs-53.json"),FileAccess.WRITE).store_string(JSON.stringify({"start":enu(start),"turn":enu(low),"finish":enu(finish),"checks":checks,"waypoints":measured,"walks":walks,"down_contacts":down,"up_contacts":up},"  "))
	quit(2 if ever_failed else 0)
