extends "../../scene_r24/day_one/verify.gd"

func spot(place: Dictionary, u: float, v: float) -> Vector3:
	var a: float = place.bearing
	var p: Array = place.east_north
	var world := Vector3(p[0] + cos(a)*u - sin(a)*v, place.height + .55, -(p[1] + sin(a)*u + cos(a)*v))
	var ray := PhysicsRayQueryParameters3D.create(world, world - Vector3.UP * 12, 1)
	var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.position + Vector3.UP * .035 if not hit.is_empty() else Vector3.INF

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	for i in 1800:
		if scene.get("gameplay"):
			break
		await physics_frame
	if not check("first_shift_loaded", scene.get("gameplay") != null):
		quit(2)
		return
	await frames(25)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var widths := {"南区路车棚修理铺":25.0, "照相巷便民市场":22.0, "江岸茶摊":21.0}
	for place: Dictionary in data.destinations:
		var width: float = widths[place.name]
		var front: float = place.front_offset - 2.35
		var left := -.27 * width
		var right := .22 * width
		var points := [spot(place,left,front-7.15),spot(place,left,front+.51),spot(place,right,front+.51),spot(place,right,front-7.15)]
		if not check(place.name + "_support", not points.has(Vector3.INF), str(points)):
			continue
		scene.explorer.begin_route_test(points.front(), points[1])
		await frames(20)
		var outward := await WalkTest._walk(scene, points.slice(1), place.name+"_out")
		check(place.name+"_out", outward["pass"], outward)
		if outward["pass"]:
			points.reverse()
			var back := await WalkTest._walk(scene, points.slice(1), place.name+"_back")
			check(place.name+"_back", back["pass"], back)
	FileAccess.open(output.path_join("destinations.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
