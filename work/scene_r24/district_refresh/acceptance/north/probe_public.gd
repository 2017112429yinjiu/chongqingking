extends "../../continuous_site_walk.gd"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var path: String = get_script().resource_path.get_base_dir().path_join("public-register.json")
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--acceptance-profile="):
			path = arg.trim_prefix("--acceptance-profile=")
	var register: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var profiles := {}
	var sightlines := {}
	var space := scene.get_world_3d().direct_space_state
	for s: Dictionary in register.stations:
		var layers := column(s.en)
		profiles[s.label] = layers
		if not s.has("heading") or not s.has("device_height_m"):
			continue
		var support := layers.filter(func(row: Array) -> bool: return row[2] > .7)
		if support.is_empty():
			continue
		var from := Vector3(s.en[0], support[0][1] + s.device_height_m, -s.en[1])
		var hits := []
		for offset: float in [-12., 0., 12.]:
			var angle := deg_to_rad(float(s.heading) + offset)
			var ray := PhysicsRayQueryParameters3D.create(from, from + 19. * Vector3(sin(angle), 0, -cos(angle)), 1)
			var hit := space.intersect_ray(ray)
			hits.append({"offset_deg":offset,"owner":str(hit.collider.get_parent().name) if not hit.is_empty() else "",
				"enu":enu(hit.position) if not hit.is_empty() else []})
		sightlines[s.label] = {"eye_enu":enu(from),"hits":hits}
	var candidates := {"42-gate-front":[89.54,190.05],"42-street-start":[85.826,188.995],
		"43-fascia-start":[105.06,162.10],"43-fascia-front":[107.30,164.62],
		"43-fascia-approach":[106.28,163.22],"43-street":[110.95,161.256]}
	for label: String in candidates:
		profiles[label] = column(candidates[label])
	FileAccess.open(output.path_join("public-edges-heights.json"), FileAccess.WRITE).store_string(JSON.stringify(
		{"camera_columns":profiles,"fixed_eye_sightlines":sightlines,
			"gameplay_waypoints_east_north":candidates,"scene":scene.scene_file_path}, "  "))
	quit()
