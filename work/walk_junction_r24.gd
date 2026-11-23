extends SceneTree

func _initialize() -> void:call_deferred("walk")

func walk() -> void:
	var main:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	while main.gameplay==null or main.street_block.tracks.size()!=8:await physics_frame
	var directory:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/road_walk")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var walker=main.explorer
	var trail: Array[Vector3]=[
		Vector3(24.7,9.01,78.15),Vector3(28.6,9.15,77.35),Vector3(33.0,9.35,76.51),
		Vector3(37.2,9.59,75.3),Vector3(40.4,9.1,76.7),Vector3(43.1,8.66,77.52),
		Vector3(47.0,9.01,76.4),Vector3(50.5,9.37,75.55),Vector3(52.8,9.15,77.55),
		Vector3(55.95,8.66,80.71),Vector3(59.6,9.15,79.04),Vector3(63.8,10.45,76.64),
		Vector3(68.4,11.15,74.02)]
	var outward:=trail.size()
	for i in range(outward-2,-1,-1):trail.append(trail[i])
	main.hud.hide()
	walker.begin_route_test(trail[0]+Vector3.UP*.15,trail[1])
	for i in 20:await physics_frame
	var prev: Vector3=walker.body.global_position
	var metres:=0.;var largest:=0.;var rows: Array=[];var blockers: Array=[]
	for idx in range(1,trail.size()):
		walker.automation_axis=Vector2(0,-1)
		var arrived:=false
		for frame in 270:
			walker.aim_route_test(trail[idx])
			await physics_frame
			var pos: Vector3=walker.body.global_position
			metres+=Vector2(pos.x-prev.x,pos.z-prev.z).length()
			largest=maxf(largest,(pos-prev).length());prev=pos
			if Vector2(pos.x-trail[idx].x,pos.z-trail[idx].z).length()<.25:
				arrived=true;break
		rows.append({"index":idx,"foot":str(prev),"arrived":arrived})
		if not arrived:
			for i in walker.body.get_slide_collision_count():
				blockers.append(str(walker.body.get_slide_collision(i).get_collider().get_parent().name))
			break
		if idx in [2,5,9,12,19,22] and DisplayServer.get_name()!="headless":
			walker.automation_axis=Vector2.ZERO
			var target:=Vector3(30.,11.64,78.04) if idx==2 else Vector3(59.7,9.85,89.6)
			if idx==9:target=Vector3(69.6,10.31,82.8)
			if idx==12:target=Vector3(58.1,9.66,80.7)
			if idx==19:target=Vector3(32.2,9.31,78.8)
			if idx==22:target=Vector3(26.,10.34,76.5)
			for frame in 20:
				walker.camera.look_at(target);walker._sync_angles()
				await physics_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(directory+"/corner_walk_%02d.png"%idx)
	walker.end_route_test()
	var ok: bool=rows.size()==trail.size()-1 and rows.back().arrived and largest<.6
	var report:={"passed":ok,"metres":metres,"max_frame_m":largest,"checkpoints":rows,"blockers":blockers}
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var report_name:="/corner_walk.json" if DisplayServer.get_name()=="headless" else "/corner_walk_visual.json"
	FileAccess.open(directory+report_name,FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("CORNER_WALK ",ok," ",metres," ",blockers)
	quit(0 if ok else 2)

