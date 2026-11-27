extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/jiefang-gate25-finish.json"

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name()!="headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	if graphics:
		scene.hud.hide()
		for arg: String in OS.get_cmdline_user_args():
			if arg.begins_with("--site-fixed-views="):
				await site_fixed_frames(arg.trim_prefix("--site-fixed-views="))
	var site: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var results := {}
	var actor = scene.explorer
	if not "--site-view-only" in OS.get_cmdline_user_args():
		var rows: Array = site.walks["25"]
		var route: Array[Vector3] = []
		var sections := []
		for i in rows.size():
			var row: Array = rows[i]
			var point := Vector3(row[0],row[2],-row[1])
			route.append(point)
			var layer := "COL_Jiefang25_JoinedFlags" if i==0 else "COL_Jiefang25_RegisteredStoneSteps"
			var layers := column(row.slice(0,2))
			var intact := layers.any(func(hit: Array) -> bool:
				return hit[0]==layer and absf(hit[1]-row[2])<.075 and hit[2]>.80)
			check("public_stair_support_%d"%i,intact,[row,layer,layers])
			sections.append({"point":row,"expected":layer,"hits":layers,"pass":intact})
		var start: Vector3 = actor.body.global_position
		check("normal_spawn_on_street_flags",actor.walking and actor.body.is_on_floor() and start.distance_to(route[0])<.23,enu(start))
		var outward := await leg_without_placement("25_street_to_exterior_door",route.slice(1))
		var reversal: Vector3 = actor.body.global_position
		var returning := {}
		if outward.pass:
			check("stopped_on_top_landing",reversal.distance_to(route[-1])<.34,enu(reversal))
			if graphics:
				actor.aim_route_test(route[-3])
				await eye_frame("25-player-look-back",null)
			route.reverse()
			returning = await leg_without_placement("25_door_back_to_street",route.slice(1))
			check("returned_to_street_flags",actor.body.global_position.distance_to(start)<.37,enu(actor.body.global_position))
		actor.end_route_test()
		results = {"sections":sections,"out":outward,"back":returning,"turn_enu":enu(reversal),
			"start_enu":enu(start),"trace":walks,"reposition_between_legs":0}
	FileAccess.open(output.path_join("gate25.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"native_frames":view_positions,"day_one_engine":Engine.get_version_info().string,
		"site":site.eye_controls,"paths":results,"checks":checks},"  "))
	quit(2 if ever_failed else 0)
