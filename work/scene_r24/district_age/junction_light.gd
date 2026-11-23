extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate();root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15);game=scene.gameplay;game.owner_scene.hud.hide()
	var cam:=Camera3D.new();scene.add_child(cam);cam.fov=61;cam.make_current()
	for v:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/views.json")):
		if v[0] not in ["fork_shoulder","north_junction_up","south_junction_up"]:continue
		cam.global_position=Vector3(v[1][0],v[1][1],v[1][2]);cam.look_at(Vector3(v[2][0],v[2][1],v[2][2]));cam.force_update_transform()
		for style in [Viewport.DEBUG_DRAW_UNSHADED,Viewport.DEBUG_DRAW_LIGHTING,Viewport.DEBUG_DRAW_NORMAL_BUFFER]:
			root.debug_draw=style;await capture(str(v[0])+str(style))
	quit()
