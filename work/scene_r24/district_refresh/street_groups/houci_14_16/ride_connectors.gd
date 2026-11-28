extends "res://../../scene_r24/day_one/verify.gd"

const Grade := preload("res://scripts/nanqu_rail_grade.gd")

const SITE := "res://assets/district_500/houci-14-16.json"

func world(row: Array) -> Vector3:
	return Vector3(row[0],row[2],-row[1])

func support(p: Vector3, above:=.52, below:=1.7) -> Dictionary:
	var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*above,p-Vector3.UP*below,1)
	var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
	return {} if hit.is_empty() else {"body":String(hit.collider.get_parent().name),"y":hit.position.y,"normal_y":hit.normal.y}

func drive(points: Array, allowed: Array, trace_merge := false) -> Dictionary:
	var start:=world(points[0])
	var face:=world(points[1])-start
	bike.global_position=start+Vector3.UP*.21
	bike.rotation=Vector3(0,atan2(-face.x,-face.z),0)
	bike.velocity=Vector3.ZERO
	bike.speed=0.
	bike.last_obstacle={}
	bike.test_throttle=0.
	bike.test_brake=true
	bike.test_steer=0.
	await frames(22)
	var stable:=bike.is_on_floor() and not bike.is_on_wall()
	var destination:=1
	var silent:=0
	var nearest:=INF
	var metres:=0.
	var air:=0
	var intended:=0
	var trail:=[]
	var merge_frames: Array = []
	for tick in 1800:
		var old: Vector3=bike.global_position
		var goal:=world(points[destination])-old
		goal.y=0.
		var gap:=goal.length()
		if gap<.62:
			destination+=1
			if destination==points.size(): break
			nearest=INF
			silent=0
			continue
		if gap<nearest-.03:
			nearest=gap
			silent=0
		else:
			silent+=1
		if silent>175: break
		var angle: float=(-bike.global_basis.z).signed_angle_to(goal.normalized(),Vector3.UP)
		bike.test_steer=clampf(angle*2.55,-1.,1.)
		var speed: float=2.25 if absf(angle)>.25 else 3.04
		bike.test_brake=bike.speed>speed+.17
		bike.test_throttle=1. if bike.speed<speed else 0.
		await physics_frame
		var p:Vector3=bike.global_position
		metres+=old.distance_to(p)
		air+=int(not bike.is_on_floor())
		var in_merge := p.x >= 202. and p.x <= 216. and -p.z >= 33. and -p.z <= 49.
		if trace_merge and (in_merge or not bike.is_on_floor()):
			var contacts: Array = []
			for i in bike.get_slide_collision_count():
				var hit: KinematicCollision3D = bike.get_slide_collision(i)
				var normal := hit.get_normal()
				var point := hit.get_position()
				contacts.append({"owner":str(hit.get_collider().get_parent().name),
					"enu":[point.x,-point.z,point.y],"normal":[normal.x,-normal.z,normal.y]})
			merge_frames.append({"tick":tick,"enu":[p.x,-p.z,p.y],"from_enu":[old.x,-old.z,old.y],
				"floor":bike.is_on_floor(),"surface":support(p),"contacts":contacts,"vertical_velocity_mps":bike.velocity.y})
		if tick%12==0:
			var contact:=support(p)
			intended+=int(contact.get("body","") in allowed)
			trail.append({"enu":[p.x,-p.z,p.y],"contact":contact})
	bike.test_brake=true
	bike.test_throttle=0.
	await frames(28)
	return {"pass":stable and destination==points.size() and intended>=int(trail.size()*.95) and air<=12,
		"reached":destination-1,"targets":points.size()-1,"distance_m":metres,"airborne_frames":air,
		"intended_surface_samples":intended,"sample_count":trail.size(),"trace":trail,"merge_frames":merge_frames,
		"last_contact":bike.last_obstacle.duplicate(true),"stable_start":stable}

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	game=scene.gameplay
	bike=game.scooter
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var results:={}
	bike.enter(game.actor)
	bike.automation=true
	for plot in ["14","16"]:
		var name:String="COL_Houci14_Road_1306489251" if plot=="14" else "COL_Houci16_Road_176968735"
		var allowed: Array=[name] if plot=="14" else [name,"COL_R24_LinkDeck_R24_link_asphalt"]
		if plot=="16" and not Grade.installed_plan(scene).is_empty():
			allowed.append("COL_NanquGrade_EastApproachingBranch")
		var data: Dictionary=plan.roads[plot]
		var rows: Array=data.drives_enu.duplicate(true)
		if plot=="16":
			rows.push_front([184.10,4.05,24.74])
			rows=Grade.adjust(scene,rows,true)
		var forward:=await drive(rows,allowed)
		rows.reverse()
		var reverse:=await drive(rows,allowed)
		results[plot]={"oneway_reverse_closed_qa":plot=="16","forward":forward,"reverse":reverse}
		check("connector_"+plot+"_forward",forward.pass,{"reached":forward.reached,"targets":forward.targets,"distance_m":forward.distance_m,"last_contact":forward.last_contact})
		check("connector_"+plot+"_reverse",reverse.pass,{"reached":reverse.reached,"targets":reverse.targets,"distance_m":reverse.distance_m,"last_contact":reverse.last_contact})
	var across: Dictionary={}
	for plot in ["14","16"]:
		var rows:=[]
		for section: Array in plan.roads[plot].across_enu:
			for pt: Array in Grade.adjust(scene,section,true) if plot=="16" else section:
				rows.append(support(world(pt),.20,.20))
		across[plot]=rows
		var name: String="COL_Houci14_Road_1306489251" if plot=="14" else "COL_Houci16_Road_176968735"
		var on_road:=0
		var coalesced:=0
		var grade_active: bool=plot=="16" and not Grade.installed_plan(scene).is_empty()
		var i:=0
		for group: Array in plan.roads[plot].across_enu:
			for pt: Array in group:
				var hit: Dictionary=rows[i]
				var body: String=hit.get("body","")
				var merge: bool=grade_active and pt[1]>=37.8 and body=="COL_NanquGrade_EastApproachingBranch"
				if (body==name or merge) and hit.get("normal_y",0.)>.72:
					on_road+=1
					coalesced+=int(merge)
				i+=1
		check("connector_"+plot+"_three_point_sections",on_road==rows.size(),{"surface_contacts":on_road,"samples":rows.size(),"shared_merge_contacts":coalesced})
	FileAccess.open(output.path_join("rides.json"),FileAccess.WRITE).store_string(JSON.stringify({"results":results,"across":across,"identity":scene.scene_identity.district_500,"checks":checks,"scene":scene.scene_file_path},"  "))
	quit(2 if ever_failed else 0)
