extends "riverside/survey.gd"
## Starts from the normal exploration spawn. The same player body walks both legs.

var view_positions := []
var graphics := false

func site_plan() -> Dictionary:
	return {}

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	graphics = DisplayServer.get_name() != "headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	for tick in 1400:
		if scene.get("gameplay"):
			break
		await physics_frame
	if not check("first_shift", scene.get("gameplay") != null):
		quit(2)
		return
	await frames(24)
	var spec := site_plan()
	var actor = scene.explorer
	var street_origin: Vector3 = actor.body.global_position
	var route: Array[Vector3] = []
	var sections := []
	for station: Array in spec.stations:
		# The controller follows horizontal goals, and physics supplies each foot height.
		route.append(Vector3(station[0],0,-station[1]))
		sections.append({"east_north":station,"contacts":column(station)})
	var spawn_error := Vector2(street_origin.x,-street_origin.z).distance_to(Vector2(spec.stations[0][0],spec.stations[0][1]))
	check("normal_street_spawn",actor.walking and actor.body.is_on_floor() and spawn_error < .14,
		{"gap_m":spawn_error,"enu":enu(street_origin)})
	if graphics:
		scene.hud.hide()
		await eye_frame("street",spec.street_focus)
	if not "--site-view-only" in OS.get_cmdline_user_args() and not ever_failed:
		var outward := await leg_without_placement(spec.id+"_out",route.slice(1))
		if outward["pass"]:
			var destination: Vector3 = actor.body.global_position
			check("on_destination_floor",absf(destination.y - float(spec.destination_y)) < .21,enu(destination))
			var reversal: Vector3 = route[-2]
			actor.aim_route_test(reversal)
			if graphics:
				await eye_frame("inside_look_back",spec.get("return_focus"))
			route.reverse()
			await leg_without_placement(spec.id+"_back",route.slice(1))
			var terminal: Vector3 = actor.body.global_position
			check("returned_to_same_street",terminal.distance_to(street_origin)<.46,enu(terminal))
			if graphics:
				await eye_frame("street_return",spec.street_focus)
		actor.end_route_test()
	FileAccess.open(output.path_join("round-trip.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"engine":Engine.get_version_info().string,
		"renderer":RenderingServer.get_current_rendering_method(),"device":RenderingServer.get_video_adapter_name(),
		"native_frames":view_positions,"sections":sections,"teleports_between_legs":0,
		"start":"normal first_shift exploration spawn","candidate":scene.scene_identity.district_500,
		"checks":checks,"walks":walks}, "  "))
	quit(2 if ever_failed else 0)

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var actor = scene.explorer
	var starting := enu(actor.body.global_position)
	var stride := [starting]
	var last_tick := [Engine.get_physics_frames()]
	var sample := func() -> void:
		var tick := Engine.get_physics_frames()
		if tick-last_tick[0]>=12:
			stride.append(enu(actor.body.global_position))
			last_tick[0] = tick
	physics_frame.connect(sample)
	var result := await WalkTest._walk(scene,goals,label)
	physics_frame.disconnect(sample)
	var finish := enu(actor.body.global_position)
	stride.append(finish)
	check(label,result["pass"],result)
	walks.append({"id":label,"start_enu":starting,"finish_enu":finish,"result":result,"trace_enu":stride})
	return result

func eye_frame(label: String, focus: Variant) -> void:
	var actor = scene.explorer
	if focus != null:
		actor.camera.look_at(Vector3(focus[0],focus[2],-focus[1]),Vector3.UP)
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var file := output.path_join(label+".png")
	var result := root.get_texture().get_image().save_png(file)
	check("frame_"+label,result==OK,file.get_file())
	view_positions.append({"frame":file.get_file(),"eye_enu":enu(actor.camera.global_position),
		"direction_xyz":str(-actor.camera.global_basis.z),"pixel_size":str(root.size)})

func enu(point: Vector3) -> Array:
	return [point.x,-point.z,point.y]
