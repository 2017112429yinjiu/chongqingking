extends "../../scene_r24/day_one/verify.gd"
const STUDY := "res://../../scene_r24/district_age/"
func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay
	var space:=scene.get_world_3d().direct_space_state
	var material_report:={}
	for m in scene.find_children("COL_B_*","MeshInstance3D",true,false):
		if m.mesh and m.is_visible_in_tree():
			var mat=m.get_active_material(0)
			if mat is ShaderMaterial and mat.shader and mat.shader.resource_path.ends_with("street_surface_r19.gdshader"):
				material_report[str(m.name)]=mat.get_shader_parameter("residential_age")
	var query_rows:Array=JSON.parse_string(FileAccess.get_file_as_string(STUDY+"queries.json"))
	var sections:=[]
	for row:Array in query_rows:
		var origin:=Vector3(row[2],row[3],row[4])
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(origin+Vector3.UP*.60,origin-Vector3.UP*2.3,1))
		sections.append([row[0],row[1],row[2],row[4],null,null] if hit.is_empty() else [row[0],row[1],row[2],row[4],snappedf(hit.position.y,.001),str(hit.collider.get_parent().name)])
	FileAccess.open(output.path_join("physics.json"),FileAccess.WRITE).store_string(JSON.stringify(sections))
	var details:Dictionary=scene.scene_identity.get("district_connections",{})
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.fov=61
	camera.cull_mask&=~game.actor.FIRST_PERSON_BODY_LAYER
	game.owner_scene.hud.hide()
	camera.make_current()
	for v:Array in JSON.parse_string(FileAccess.get_file_as_string(STUDY+"views.json")):
		camera.global_position=Vector3(v[1][0],v[1][1],v[1][2])
		camera.look_at(Vector3(v[2][0],v[2][1],v[2][2]))
		camera.force_update_transform()
		await process_frame
		RenderingServer.camera_set_transform(camera.get_camera_rid(),camera.global_transform)
		await capture(v[0])
	FileAccess.open(output.path_join("scene.json"),FileAccess.WRITE).store_string(JSON.stringify({"district":details,"profile":scene.art_profile.get("art_revision"),"walls":material_report,"checks":checks}))
	quit(2 if ever_failed else 0)
