extends "../../continuous_site_walk.gd"

const RAYS := "56-opening-plan.json"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(get_script().resource_path.get_base_dir().path_join(RAYS)))
	var space := scene.get_world_3d().direct_space_state
	var hits := []
	for eye: Dictionary in cfg.stations:
		var e: Array = eye.enu
		var column_hits := column(e)
		var road: Array = column_hits.filter(func(row: Array) -> bool: return String(row[0]).begins_with("COL_Outer500_Surface_") and row[2] > .7)
		check("station_lower_road_" + eye.id, not road.is_empty(), column_hits)
		if road.is_empty():
			continue
		var from := Vector3(e[0], road[0][1] + cfg.device_height_m, -e[1])
		var heading := deg_to_rad(float(eye.heading))
		var pitch := deg_to_rad(float(cfg.pitch))
		var f := float(cfg.pixels[1]) * .5 / tan(deg_to_rad(float(cfg.fovy)) * .5)
		var forward := Vector3(sin(heading)*cos(pitch),sin(pitch),-cos(heading)*cos(pitch))
		var right := Vector3(cos(heading),0,sin(heading))
		var camera_up := right.cross(forward)
		for feature: String in eye.targets:
			var px: Array = eye.targets[feature]
			var direction := (forward + right * ((float(px[0]) - float(cfg.pixels[0])*.5)/f) + camera_up * ((float(cfg.pixels[1])*.5-float(px[1]))/f)).normalized()
			var loc: Array = cfg.features[feature]
			var horizontal := Vector2(from.x,-from.z).distance_to(Vector2(loc[0],loc[1]))
			var target := from + direction * (horizontal / Vector2(direction.x,direction.z).length())
			var query := PhysicsRayQueryParameters3D.create(from,target+direction*.25,1)
			var result := space.intersect_ray(query)
			hits.append({"station":eye.id,"feature":feature,"pixel":px,"from":enu(from),"projected_target":enu(target),
				"target_plan":loc,"rise_m":target.y-from.y,"support":road[0],
				"first_hit":({"owner":str(result.collider.get_parent().name),"at":enu(result.position),
					"distance_m":result.position.distance_to(from),"remaining_m":result.position.distance_to(target)}
					if not result.is_empty() else {})})
	FileAccess.open(output.path_join("56-opening-rays.json"),FileAccess.WRITE).store_string(JSON.stringify({"hits":hits,
		"checks":checks,"scene":scene.scene_file_path,"scene_assets":scene.scene_identity.district_500,"engine":Engine.get_version_info().string},"  "))
	quit(2 if ever_failed else 0)
