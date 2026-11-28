extends "../../continuous_site_walk.gd"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var support := column([110.95106333310167, 161.25602223941422])
	var eye := Vector3(110.95106333310167, 38.247, -161.25602223941422)
	var heading := deg_to_rad(329.)
	var forward := Vector3(sin(heading), 0., -cos(heading))
	var right := Vector3(cos(heading), 0., sin(heading))
	var f := 220. / tan(deg_to_rad(35.))
	var space := scene.get_world_3d().direct_space_state
	var rows := []
	for px: Vector2 in [Vector2(350,220),Vector2(355,248),Vector2(417,230),Vector2(470,251),Vector2(143,219)]:
		var dir := (forward+right*((px.x-350.)/f)+Vector3.UP*((220.-px.y)/f)).normalized()
		var query := PhysicsRayQueryParameters3D.create(eye,eye+22.*dir,1)
		query.hit_back_faces = true
		var first := space.intersect_ray(query)
		rows.append({"pixel":[px.x,px.y],"eye_enu":enu(eye),"direction_enu":enu(dir),
			"first_hit":({"owner":str(first.collider.get_parent().name),"at":enu(first.position),
				"normal_enu":enu(first.normal),"distance_m":eye.distance_to(first.position)}
				if not first.is_empty() else {})})
	FileAccess.open(output.path_join("43-same-pixel.json"),FileAccess.WRITE).store_string(JSON.stringify(
		{"station":"09029200121906291519265961L","fov_degrees":70,"heading":329,
			"pixels":[700,440],"local_road_layers":support,"head_height_m":2.32,"hits":rows,
			"scene_assets":scene.scene_identity.district_500}, "  "))
	quit()
