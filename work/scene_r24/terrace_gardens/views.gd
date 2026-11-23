extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.fov=61
	camera.cull_mask&=~game.actor.FIRST_PERSON_BODY_LAYER
	game.owner_scene.hud.hide()
	camera.make_current()
	for v:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/terrace_gardens/views.json")):
		camera.global_position=Vector3(v[1][0],v[1][1],v[1][2])
		camera.look_at(Vector3(v[2][0],v[2][1],v[2][2]))
		camera.force_update_transform()
		await process_frame
		RenderingServer.camera_set_transform(camera.get_camera_rid(),camera.global_transform)
		await capture(v[0])
	FileAccess.open(output.path_join("scene.json"),FileAccess.WRITE).store_string(JSON.stringify({"revision":scene.art_profile.get("art_revision"),"layer":scene.scene_identity.get("district_connections",{}),"checks":checks}))
	quit(2 if ever_failed else 0)
