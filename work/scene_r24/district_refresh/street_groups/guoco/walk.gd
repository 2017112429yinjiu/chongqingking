extends "../../riverside/survey.gd"

const PLAN := "res://assets/district_500/guoco-frontages.json"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var heights := {}
	var profiles := {}
	var direct := scene.get_world_3d().direct_space_state
	for name: String in plan.towers:
		var tower: Dictionary = plan.towers[name]
		var p := Vector2.ZERO
		for q: Array in tower.outline_east_north:
			p += Vector2(q[0],q[1]) / tower.outline_east_north.size()
		var ray := PhysicsRayQueryParameters3D.create(Vector3(p.x,260,-p.y),Vector3(p.x,-20,-p.y),1)
		var hit := direct.intersect_ray(ray)
		var collider := "COL_Guoco_%s_%d" % [name,int(tower.way)]
		var ok := not hit.is_empty() and String(hit.collider.get_parent().name) == collider
		var y := float(hit.position.y) if ok else 0.
		ok = ok and absf(y-float(tower.roof_game_m)+.34) < .035
		heights[name] = {"solid_roof_m":y,"visual_roof_m":tower.roof_game_m,"ground":tower.terrain_min_max_m}
		check("tower_"+name+"_upper_body",ok,heights[name])
	for n: String in plan.retired_objects:
		check("old_mesh_removed_"+n, scene.find_child(n,true,false)==null)
	var under := ground_point([192,-73],.05)
	var head := direct.intersect_ray(PhysicsRayQueryParameters3D.create(under,under+Vector3.UP*9.,1))
	var clear := float(head.position.y)-under.y if not head.is_empty() else -1.
	check("podium_pedestrian_headroom",clear>3.6 and clear<6.,clear)
	for route: String in plan.ground_walks:
		var path: Array[Vector3] = []
		var trace := []
		for station: Array in plan.ground_walks[route]:
			path.append(ground_point(station,.04))
			trace.append({"east_north":station,"layers":column(station)})
		profiles[route] = trace
		await walk_pair(route,path)
	FileAccess.open(output.path_join("guoco.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"candidate":scene.scene_identity.district_500,"towers":heights,
		"checks":checks,"walks":walks,"sections":profiles},"  "))
	quit(2 if ever_failed else 0)
