extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(10)
	var cam:=Camera3D.new();scene.add_child(cam);cam.fov=61;cam.make_current()
	cam.global_position=Vector3(-43.7,7.13,97.15);cam.look_at(Vector3(-50.45,6.46,92.2));cam.force_update_transform()
	var result:=[]
	for p:Vector2 in [Vector2(895,255),Vector2(825,245),Vector2(759,252),Vector2(633,251),Vector2(605,250),Vector2(559,246),Vector2(524,242),Vector2(509,243),Vector2(460,239),Vector2(417,234)]:
		var origin:=cam.global_position;var normal:=cam.project_ray_normal(p*root.get_visible_rect().size/Vector2(960,540))
		var hit:=scene.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,origin+normal*120.,1))
		if hit:result.append([str(p),str(hit.collider.get_parent().name),str(hit.position)])
	FileAccess.open(output.path_join("bank.json"),FileAccess.WRITE).store_string(JSON.stringify(result));quit()
