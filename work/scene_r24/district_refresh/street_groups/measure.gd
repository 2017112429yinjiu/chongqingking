extends "../riverside/survey.gd"
## Sample physical ground, decks and building collisions at registered sites.

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var registration_path := OS.get_environment("CQ_STREET_GROUP_REGISTRATION")
	if registration_path.is_empty():
		registration_path = get_script().resource_path.get_base_dir().path_join("run/plot-registration.json")
	var scope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(registration_path))
	var results := []
	for plot: Dictionary in scope.plots:
		var crossing_profiles := []
		var wall_profiles := []
		for crossing: Dictionary in plot.roads:
			var samples := []
			var points: Array = crossing.east_north
			for i in points.size():
				var before := to_vector(points[maxi(0, i - 1)])
				var after := to_vector(points[mini(points.size() - 1, i + 1)])
				var axis := (after - before).normalized().orthogonal()
				samples.append(profile(points[i], axis))
			crossing_profiles.append({"way": crossing.way, "samples": samples})
		for feature: Dictionary in plot.buildings:
			if feature.side_stations_east_north.is_empty():
				continue
			for side: Array in feature.side_stations_east_north:
				var samples := []
				var axis := (to_vector(side[-1]) - to_vector(side[0])).normalized().orthogonal()
				for point: Array in side:
					samples.append(profile(point, axis))
				wall_profiles.append({"way": feature.way, "samples": samples})
		results.append({"plot": plot.plot, "centre": profile(plot.centre_east_north, Vector2.ZERO),
			"road_profiles": crossing_profiles, "building_profiles": wall_profiles})
	var street_profiles := {}
	var street_routes := {}
	if "--walk-registered-streets" in OS.get_cmdline_user_args():
		for way: String in ["59146654", "1025797976", "1025797980"]:
			var points: Array = scope.ways[way].east_north
			var samples := []
			var path: Array[Vector3] = []
			for i in range(points.size() - 1):
				var start := to_vector(points[i])
				var finish := to_vector(points[i+1])
				var transverse := (finish-start).normalized().orthogonal()
				var count := maxi(1, ceili(start.distance_to(finish)/3.0))
				for step in count:
					var p := start.lerp(finish, float(step)/count)
					var en := [p.x,p.y]
					samples.append(profile(en, transverse))
					if absf(p.x) < 249.0 and absf(p.y) < 249.0:
						path.append(ground_point(en, .045))
			var last := to_vector(points[-1])
			var tangent := (last - to_vector(points[-2])).normalized()
			samples.append(profile(points[-1], tangent.orthogonal()))
			if absf(last.x) < 249.0 and absf(last.y) < 249.0:
				path.append(ground_point(points[-1], .045))
			if path.size() > 1:
				await walk_pair("osm_"+way, path)
				street_routes[way] = path
			street_profiles[way] = samples
	if "--walk-joined-streets" in OS.get_cmdline_user_args():
		var route: Array[Vector3] = street_routes["59146654"].duplicate()
		var link: Array[Vector3] = street_routes["1025797976"]
		var lane: Array[Vector3] = street_routes["1025797980"]
		var junction := link.find(lane[0])
		assert(route[-1].is_equal_approx(link[0]) and junction > 0)
		route.append_array(link.slice(1, junction + 1))
		route.append_array(lane.slice(1))
		await walk_pair("joined_streets", route)
	var measurements := {"outer": scene.scene_identity.get("district_500", {}),
		"source_sha256": scope.source_sha256, "plots": results,
		"streets": street_profiles, "walks": walks, "checks": checks}
	var file := FileAccess.open(output.path_join("street_group_profiles.json"), FileAccess.WRITE)
	assert(file)
	file.store_string(JSON.stringify(measurements, "  "))
	quit(2 if ever_failed else 0)

func profile(point: Array, cross: Vector2) -> Dictionary:
	var samples := []
	var offsets := [0.0] if cross.is_zero_approx() else [-2.5, -1.2, 0.0, 1.2, 2.5]
	for offset: float in offsets:
		var location := to_vector(point) + cross * offset
		var coordinates := [snappedf(location.x, 0.001), snappedf(location.y, 0.001)]
		samples.append({"offset_m": offset, "east_north": coordinates, "hits": column(coordinates),
			"inside_playable_box": absf(location.x) <= 250 and absf(location.y) <= 250})
	return {"east_north": point, "samples": samples}

func to_vector(point: Array) -> Vector2:
	return Vector2(point[0], point[1])
