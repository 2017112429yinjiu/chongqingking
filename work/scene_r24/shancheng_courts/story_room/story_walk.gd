extends "../../../scene_r24/outer_neighborhood/market_entry.gd"

var ring:=PackedVector2Array()
var span: float
var depth: float
var floor_y: float

func local_spot(x: float,y: float,z: float) -> Vector3:
	var en:=ring[0].lerp(ring[1],x/span).lerp(ring[3].lerp(ring[2],x/span),y/depth)
	return Vector3(en.x,floor_y+z,-en.y)

func study_object(target: Vector3) -> void:
	var actor=scene.explorer
	var eye: Vector3=actor.camera.global_position
	var start: Vector3=-actor.camera.global_basis.z
	var goal:=eye.direction_to(target)
	for i in range(1,37):
		var dir:=start.slerp(goal,smoothstep(0.,1.,i/36.))
		actor.camera.look_at(actor.camera.global_position+dir,Vector3.UP)
		actor._sync_angles()
		await physics_frame
	await frames(46)

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	var graphics:=DisplayServer.get_name()!="headless"
	if graphics: RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.get("gameplay"): await physics_frame
	await frames(30)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	var room: Dictionary=data.buildings.filter(func(b):return b.id=="jinma_classrooms")[0]
	for p: Array in room.ring:ring.append(Vector2(p[0],p[1]))
	span=ring[0].distance_to(ring[1])
	depth=(ring[0].distance_to(ring[3])+ring[1].distance_to(ring[2]))*.5
	floor_y=room.floor
	var collection:=scene.find_child("Court_Jinma_Story_Collection",true,false) as MeshInstance3D
	var print_found:=false
	if collection:
		for i in collection.mesh.get_surface_count():
			var mat:=collection.get_active_material(i) as BaseMaterial3D
			if mat and mat.albedo_texture and mat.albedo_texture.get_size()==Vector2(2048,1536):print_found=true
	check("original_collection_prints_imported",print_found)
	var lights: Array=[]
	for lamp: SpotLight3D in scene.find_children("Story*exhibit*spot*", "SpotLight3D", true, false):
		lights.append({"name":str(lamp.name),"energy":lamp.light_energy,"shadow":lamp.shadow_enabled})
	check("imported_track_lighting",lights.size()==2 and lights.all(func(l):return l.energy>0 and l.energy<5 and l.shadow),{"spots":lights})
	var fixture:=scene.find_child("COL_Court_Jinma_Story_Furniture",true,false)
	check("display_furniture_has_physics",fixture!=null and fixture.get_node_or_null("CQ_StaticCollision")!=null)
	var actor=scene.explorer
	actor.begin_route_test(local_spot(span*.5,-.75,.055),local_spot(span*.5,2,1.55))
	await frames(20)
	if graphics:
		recording=true
		record_tick()
	# Continuous visit with two stops, using the same player body and camera.
	var legs: Array=[
		[[span*.5,.90],[17.65,1.47],[19.28,1.41],[20.16,1.46]],
		[[22.57,1.41],[23.45,2.00],[23.43,3.54]],
		[[22.42,3.82],[19.19,3.82],[19.19,5.30],[17.82,6.62],[17.82,7.95]]]
	var lengths:=0.
	for i in legs.size():
		var path: Array=[]
		for p: Array in legs[i]:path.append(local_spot(p[0],p[1],.045))
		var result:=await WalkTest._walk(scene,path,["door_to_ticket_stand","window_to_end_display","display_to_stair"][i])
		check(result.name,result["pass"],result)
		lengths+=float(result.distance_m)
		if not result["pass"]:break
		if i==0:await study_object(local_spot(8*span/13,.69,1.02))
		if i==1:await study_object(local_spot(24.72,2.55,1.55))
	check("arrived_at_stair",actor.body.global_position.distance_to(local_spot(17.82,7.95,.045))<.36,{"walk_m":lengths})
	var foot: Vector3=actor.body.global_position
	var heading: Vector3=-actor.camera.global_basis.z
	var end: Vector3=(local_spot(20.16,2.47,1.5)-actor.camera.global_position)
	var start_angle:=atan2(heading.x,heading.z)
	var end_angle:=atan2(end.x,end.z)
	# Turn the live player camera with the feet planted at the bottom tread.
	for i in range(1,76):
		var angle:=lerp_angle(start_angle,end_angle,smoothstep(0.,1.,i/75.))
		actor.aim_route_test(foot+Vector3(sin(angle),0,cos(angle))*5.)
		await physics_frame
	await study_object(local_spot(20.16,2.47,1.16))
	await frames(18)
	recording=false
	var rotated:=absf(rad_to_deg(angle_difference(start_angle,end_angle)))
	check("look_back_from_stair_foot",rotated>120 and foot.distance_to(actor.body.global_position)<.03,
		{"turn_degrees":rotated,"foot_shift_m":foot.distance_to(actor.body.global_position),"end":str(foot)})
	if graphics:
		RenderingServer.force_draw(false,1./60.)
		root.get_texture().get_image().save_png(output.path_join("look_back.png"))
		scene.hud.hide()
		await shot("exhibit_corner",local_spot(18.10,3.51,1.60),local_spot(24.58,1.85,1.20))
		await shot("window_collection",local_spot(22.15,1.86,1.53),local_spot(22.43,.71,.96))
		await shot("glass_case",local_spot(22.98,1.33,1.38),local_spot(23.40,.72,.924))
		await shot("fare_box",local_spot(8*span/13-.21,1.04,1.31),local_spot(8*span/13,.69,1.035))
		await shot("reverse_cabinets",local_spot(23.84,1.18,1.57),local_spot(20.22,4.29,1.04))
	FileAccess.open(output.path_join("story_walk.json"),FileAccess.WRITE).store_string(JSON.stringify(
		{"checks":checks,"physics_hz":Engine.physics_ticks_per_second,"ticks_per_image":9,"images":saved_frames},"  "))
	quit(2 if ever_failed else 0)
