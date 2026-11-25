extends "../../scene_r24/outer_neighborhood/survey.gd"

func paved_route(start: Vector3, finish: Vector3, planting: Array) -> Array:
	var a := Vector2(start.x, -start.z)
	var b := Vector2(finish.x, -finish.z)
	var direction := a.direction_to(b)
	var normal := Vector2(-direction.y, direction.x)
	var length := a.distance_to(b)
	var stations := []
	for tree: Dictionary in planting:
		var root_xy := Vector2(tree.east_north_up[0], tree.east_north_up[1])
		var along := (root_xy - a).dot(direction)
		var across := (root_xy - a).dot(normal)
		if along < 1.5 or along > length - 1.5 or absf(across) > 0.54:
			continue
		# Walk inside the existing 1.88 m paving, on the wider side of its tree.
		var side := -0.60 if across > 0.0 else 0.60
		for offset: float in [-1.25, 1.25]:
			var station := along + offset
			stations.append([station, a + direction * station + normal * side])
	stations.sort_custom(func(left: Array, right: Array) -> bool: return left[0] < right[0])
	var points := [start]
	for entry: Array in stations:
		var xy: Vector2 = entry[1]
		points.append(public_floor([xy.x, xy.y], lerpf(start.y, finish.y, entry[0] / length)))
	points.append(finish)
	return points

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in 1600:
		if scene.get("gameplay"):break
		await physics_frame
	await frames(24)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for lane: Dictionary in data.lanes:
		if lane.type!="shared":continue
		var from: Dictionary=data.plots[lane.plots[0]]
		var to: Dictionary=data.plots[lane.plots[1]]
		var name:="lane_%d_%d"%[from.plot_id,to.plot_id]
		var points: Array=[]
		for i in range(lane.points.size()-1):
			var a:=public_floor(lane.points[i],lerpf(from.height,to.height,float(i)/(lane.points.size()-1)))
			var b:=public_floor(lane.points[i+1],lerpf(from.height,to.height,float(i+1)/(lane.points.size()-1)))
			var leg: Array=[a,b]
			if not leg.has(Vector3.INF) and not "--straight" in OS.get_cmdline_user_args():
				leg=paved_route(a,b,data.planting)
			points.append_array(leg if points.is_empty() else leg.slice(1))
		if points.has(Vector3.INF):
			check(name+"_floor",false,points)
			continue
		await trial(name,points)
	for plot: Dictionary in data.plots:
		if not plot.has("court"):continue
		var c: Dictionary=plot.court
		var h: float=c.upper_m
		var room_one:=world(plot,c.room_u,c.room_v,h+.04)
		var gallery_one:=world(plot,c.room_u,c.landing_v,h+.04)
		var gallery_two:=world(plot,c.other_room_u,c.landing_v,h+.04)
		var room_two:=world(plot,c.other_room_u,c.room_v,h+.04)
		await trial("neighbors_%02d"%plot.plot_id,[room_one,gallery_one,gallery_two,room_two])
	FileAccess.open(output.path_join("shared_paths.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
