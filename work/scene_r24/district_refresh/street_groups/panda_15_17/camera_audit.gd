extends "res://../../scene_r24/day_one/verify.gd"

func q_enu(p: Vector3) -> Array:
	return [p.x,-p.z,p.y]

func p_enu(p: Array) -> Vector3:
	return Vector3(p[0],p[2],-p[1])

func screenshot(name: String) -> int:
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	return root.get_texture().get_image().save_png(output.path_join(name+".png"))

func verify() -> void:
	RenderingServer.render_loop_enabled = false
	output = preload("res://scripts/qa_context.gd").directory()
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	var player=scene.explorer
	var scene_mask: int=player.FIRST_PERSON_BODY_LAYER
	var body: Node3D=player.body_view
	var meshes: Array[Node]=body.find_children("*","MeshInstance3D",true,false)
	var recorded: Array=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_refresh/street_groups/panda_15_17/views.json"))
	var view: Dictionary=recorded[0]
	var fixed := Camera3D.new()
	scene.add_child(fixed)
	fixed.global_position=p_enu(view.eye_enu)
	fixed.look_at(p_enu(view.target_enu))
	fixed.fov=view.fov_deg
	fixed.make_current()
	var old_mask := fixed.cull_mask
	var old_transform := fixed.global_transform
	var previous := await screenshot("15-fixed-default-cull")
	fixed.cull_mask &= ~scene_mask
	var after := await screenshot("15-fixed-player-layer-excluded")
	player.camera.make_current()
	var normal := await screenshot("15-normal-playing-eye")
	check("camera_matrix_held",fixed.global_transform==old_transform)
	check("cull_bit_identified",(old_mask & scene_mask)!=0 and (fixed.cull_mask & scene_mask)==0 and not meshes.is_empty() and meshes.all(func(mesh: Node) -> bool: return mesh.layers==scene_mask))
	check("normal_gameplay_controls",player.walking and player.body.is_on_floor() and player.camera.is_current() and body.visible)
	check("all_native_saves",previous==OK and after==OK and normal==OK)
	var data := {"checks":checks,"view":view,"fixed_camera_eye_enu":q_enu(fixed.global_position),"ordinary_camera_eye_enu":q_enu(player.camera.global_position),
		"player_origin_enu":q_enu(player.body.global_position),"fixed_to_player_m":fixed.global_position.distance_to(player.body.global_position),
		"first_person_layer":scene_mask,"fixed_mask_before":old_mask,"fixed_mask_after":fixed.cull_mask,"normal_mask":player.camera.cull_mask,
		"normal_control_mode":player.walking,"mesh_names":meshes.map(func(mesh: Node) -> String: return String(mesh.name)),
		"renderer":RenderingServer.get_current_rendering_method(),"device":RenderingServer.get_video_adapter_name(),"identity":scene.scene_identity.district_500}
	FileAccess.open(output.path_join("camera-audit.json"),FileAccess.WRITE).store_string(JSON.stringify(data,"  "))
	quit(2 if ever_failed else 0)
