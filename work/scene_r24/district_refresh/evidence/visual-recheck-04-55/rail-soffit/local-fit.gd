extends "res://../../scene_r24/district_refresh/continuous_site_walk.gd"

func engine_point(east:float,north:float,height:float)->Vector3:
	return Vector3(east,height,-north)

func en_cross(north:float,across:float,above:float)->Vector3:
	var west := -138.70+(-48.39-north)*.1759
	var east := -116.60+(-44.55-north)*.1759
	return engine_point(lerpf(west,east,across),north,15.23-.013*(north+93.70)+above)

func face(surface:SurfaceTool,a:Vector3,b:Vector3,c:Vector3,d:Vector3)->void:
	for v:Vector3 in [a,b,c,a,c,d]: surface.add_vertex(v)

func fit_surface(profile:Array,material:StandardMaterial3D)->MeshInstance3D:
	var loft := SurfaceTool.new()
	loft.begin(Mesh.PRIMITIVE_TRIANGLES)
	for index in profile.size():
		var a:Array=profile[index]
		var b:Array=profile[(index+1)%profile.size()]
		face(loft,en_cross(-69.,a[0],a[1]),en_cross(-117.,a[0],a[1]),
			en_cross(-117.,b[0],b[1]),en_cross(-69.,b[0],b[1]))
	loft.generate_normals()
	var ob:=MeshInstance3D.new()
	ob.mesh=loft.commit()
	ob.material_override=material
	return ob

func steel_finish(color:Color)->StandardMaterial3D:
	var mat:=StandardMaterial3D.new()
	mat.albedo_color=color
	mat.cull_mode=BaseMaterial3D.CULL_DISABLED
	mat.roughness=.85
	return mat

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	var path: String
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--fit-camera="): path=arg.trim_prefix("--fit-camera=")
	var views: Array=JSON.parse_string(FileAccess.get_file_as_string(path))
	var spec: Dictionary=views[0].duplicate()
	var camera:=Camera3D.new()
	camera.cull_mask=scene.explorer.camera.cull_mask
	scene.add_child(camera); camera.make_current()
	var eye:Array=spec.eye_enu
	var target:Array=spec.target_enu
	camera.position=engine_point(eye[0],eye[1],eye[2]); camera.look_at(engine_point(target[0],target[1],target[2])); camera.fov=spec.fov_deg
	await process_frame
	RenderingServer.force_draw(false,1./60.)
	var parent:=root.get_texture().get_image().save_png(output.path_join("04-published-camera-before.png"))
	var draft:=Node3D.new(); draft.name="QA_only_hypothetical_rail_visible_layer"
	scene.add_child(draft)
	draft.add_child(fit_surface([[0.,2.47],[0.,1.10],[.09,.21],[.21,0.],[.79,0.],[.91,.21],[1.,1.10],[1.,2.47]],steel_finish(Color(.32,.35,.36))))
	draft.add_child(fit_surface([[.026,2.44],[.029,3.52],[.094,4.33],[.21,4.56],[.79,4.56],[.906,4.33],[.971,3.52],[.974,2.44]],steel_finish(Color(.77,.80,.81))))
	var strut:=steel_finish(Color(.24,.28,.30))
	for k in range(7):
		var a:=.23+k*.088
		draft.add_child(fit_surface([[a,0.],[a,-.19],[a+.009,-.19],[a+.009,0.]],strut))
	await process_frame
	RenderingServer.force_draw(false,1./60.)
	var rough:=root.get_texture().get_image().save_png(output.path_join("04-low-soffit-only-experiment.png"))
	FileAccess.open(output.path_join("experiment.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"kind":"isolated visible-only lower-soffit fit; unresolved grade at both ends; not installed in gameplay",
		"camera":spec,"projected_far_midline_game_y_m":15.23,"same_published_colliders":true,
		"parent_code":parent,"draft_code":rough},"  "))
	quit(0 if parent==OK and rough==OK else 2)
