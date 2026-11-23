extends "../../scene_r24/day_one/verify.gd"
func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory("res://verification_r24/road_shift/court")
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(8)
	game=scene.gameplay
	var space:=scene.get_world_3d().direct_space_state
	var samples:Array=[]
	var missing:=0
	var wrong:=0
	var excluded:Array[RID]=[]
	# Sample the walking surface underneath the two collection racks as well.
	for site:Node3D in game.lesson.shelves:
		for body:Node in site.get_children():
			if body is StaticBody3D:excluded.append(body.get_rid())
	var biggest:=0.
	for x in range(-47,-22,2):
		var old:=0.
		for i in 65:
			var z:=17.6+float(i)*.08
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,18,z),Vector3(x,14,z),1)
			ray.exclude=excluded
			var hit:=space.intersect_ray(ray)
			if hit.is_empty():missing+=1;continue
			var body:String=str(hit.collider.get_parent().name)
			if not body.begins_with("COL_Terrain_200m"):wrong+=1
			var y:float=hit.position.y
			if i>0:biggest=maxf(biggest,absf(y-old))
			old=y
			samples.append([x,z,y,body])
	check("old_ribbon_retired_physics_and_view",missing==0 and wrong==0 and biggest<.075,{"n":samples.size(),"missing":missing,"other":wrong,"max_rise_over_8cm":biggest})
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.fov=64
	camera.cull_mask&=~game.actor.FIRST_PERSON_BODY_LAYER
	game.owner_scene.hud.hide()
	camera.make_current()
	for view in [["court_wall_walk",Vector3(-44,17.9,23.65),Vector3(-25,16.5,18.55)],["seam_across",Vector3(-34,17.68,24.1),Vector3(-34,16.43,19.1)],["public_slope",Vector3(-25.6,16.85,28.4),Vector3(-25.9,14.80,37)]]:
		camera.global_position=view[1]
		camera.look_at(view[2])
		camera.force_update_transform()
		await process_frame
		RenderingServer.camera_set_transform(camera.get_camera_rid(),camera.global_transform)
		await capture(view[0])
	FileAccess.open(output.path_join("cross_sections.json"),FileAccess.WRITE).store_string(JSON.stringify({"samples":samples,"checks":checks}))
	quit(2 if ever_failed else 0)
