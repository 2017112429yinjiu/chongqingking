extends "../survey.gd"

const PAVING := "COL_Outer500_WestCourt_Paving"
const SITE := "res://assets/district_500/west-court.json"
const TRAIL_WEST := [-157.9, -197.46]
const TRAIL_EAST := [-135.8, -200.87]

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	check_lamp(plan.relocated_lamp)
	var deck := []
	for e: int in range(-151, -139):
		for n: int in range(-188, -179):
			var layers := support([e, n])
			deck.append({"en": [e, n], "hit": layers})
	check("deck_continuous_level_support", deck.all(func(sample: Dictionary) -> bool:
		return not sample.hit.is_empty() and sample.hit[0][0] == PAVING and absf(sample.hit[0][1] - plan.deck_elevation_m) < .012), deck.size())
	var stair := []
	for i in plan.stair_polygons.size():
		var tread: Array = plan.stair_polygons[i]
		var toe := (xy(tread[0]) + xy(tread[1])) * .5
		var nosing := (xy(tread[2]) + xy(tread[3])) * .5
		var mid := toe.lerp(nosing, .995 if i == 0 else .5)
		stair.append({"en": [mid.x, mid.y], "hit": support([mid.x, mid.y])})
	var step_rises := []
	for i in range(1, stair.size()):
		var lower: Array = stair[i - 1].hit
		var upper: Array = stair[i].hit
		if not lower.is_empty() and not upper.is_empty() and upper[0][0] == PAVING:
			step_rises.append(upper[0][1] - lower[0][1])
	check("west_stair_profile", step_rises.size() == int(plan.stair_count) and step_rises.all(func(delta: float) -> bool:
		return delta > .12 and delta < .17), step_rises)
	var ramp := []
	var polygon: Array = plan.ramp_polygon
	for t: float in [.05, .2, .4, .6, .8, .95]:
		var a := xy(polygon[0]).lerp(xy(polygon[3]), t)
		var b := xy(polygon[1]).lerp(xy(polygon[2]), t)
		for cross: float in [.18, .5, .82]:
			var p := a.lerp(b, cross)
			ramp.append({"en": [p.x, p.y], "hit": support([p.x, p.y])})
	check("east_ramp_full_width_support", ramp.all(func(sample: Dictionary) -> bool:
		return not sample.hit.is_empty() and sample.hit[0][0] == PAVING and sample.hit[0][2] > .93), ramp.size())
	for route_name: String in plan.walk_plan:
		var points: Array = plan.walk_plan[route_name].duplicate()
		points.push_front(TRAIL_EAST if route_name == "ramp" else TRAIL_WEST)
		if route_name == "through":
			points.append(TRAIL_EAST)
		var stations: Array[Vector3] = []
		for point: Array in points:
			var floor := support(point)
			if floor.is_empty():
				break
			stations.append(Vector3(point[0], floor[0][1] + .04, -point[1]))
		check(route_name + "_stations", stations.size() == points.size(), stations.size())
		if stations.size() == points.size():
			await walk_pair(route_name, stations)
	FileAccess.open(output.path_join("west-court.json"), FileAccess.WRITE).store_string(JSON.stringify({
		"engine": Engine.get_version_info().string, "scene": scene.scene_file_path, "candidate": scene.scene_identity.district_500,
		"deck": deck, "stair": stair, "ramp": ramp, "checks": checks, "walks": walks}, "  "))
	quit(2 if ever_failed else 0)

func xy(point: Array) -> Vector2:
	return Vector2(point[0], point[1])

func support(point: Array) -> Array:
	return column(point).filter(func(hit: Array) -> bool:
		return hit[0] == PAVING or String(hit[0]).begins_with("COL_Outer500_Surface_"))

func check_lamp(fit: Dictionary) -> void:
	var old: Array = fit.old_east_north_up
	var now: Array = fit.new_east_north_up
	var previous := Vector3(old[0], old[2], -old[1])
	var placed := Vector3(now[0], now[2], -now[1])
	var furniture := scene.find_child("Outer500_Street_furniture", true, false) as MeshInstance3D
	var low := INF
	var old_vertices := 0
	for v: Vector3 in furniture.mesh.get_faces():
		var p := furniture.to_global(v)
		if absf(p.x - previous.x) < .09 and absf(p.z - previous.z) < .09 and p.y > previous.y - .01:
			old_vertices += 1
		if absf(p.x - placed.x) < .09 and absf(p.z - placed.z) < .09 and p.y > placed.y - .12:
			low = minf(low, p.y)
	var floor := support([placed.x, -placed.z])
	var clearance: float = low - float(floor[0][1]) if not floor.is_empty() and is_finite(low) else INF
	check("legacy_lamp_relocated_to_trail_support", old_vertices == 0 and absf(clearance) < .012,
		{"old_root_vertices": old_vertices, "base_clearance_m": clearance if is_finite(clearance) else null})
