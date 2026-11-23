extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	var materials:={}
	for key in ["COL_Terrain_200m_pavement","COL_Terrain_200m_yard_concrete","COL_Road_176034707_0_pavement","COL_Terrace21_Fork","COL_D18_NanquShoulder","COL_Terrain_200m_ground_dirt","COL_Terrace21_Bed00"]:
		var node:=scene.find_child(key,true,false) as MeshInstance3D
		if not node or not node.mesh:continue
		materials[key]=[]
		for i in node.mesh.get_surface_count():
			var mat=node.get_active_material(i)
			materials[key].append([str(mat),mat.shader.resource_path if mat is ShaderMaterial and mat.shader else "",str(mat.get_shader_parameter("terrace_neighbor")) if mat is ShaderMaterial else "","%s" % mat.resource_name])
	var cam:=Camera3D.new()
	scene.add_child(cam)
	cam.fov=61.
	var space:=scene.get_world_3d().direct_space_state
	var results:={}
	for v:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/terrace_gardens/views.json")):
		cam.global_position=Vector3(v[1][0],v[1][1],v[1][2])
		cam.look_at(Vector3(v[2][0],v[2][1],v[2][2]))
		results[v[0]]=[]
		for uv:Vector2 in [Vector2(.12,.85),Vector2(.24,.83),Vector2(.54,.83),Vector2(.56,.98),Vector2(.9,.88),Vector2(.05,.49),Vector2(.32,.45),Vector2(.25,.38),Vector2(.4,.46),Vector2(.6,.45)]:
			var ray:Vector3=cam.global_basis*(Vector3((uv.x-.5)*2.*16./9.*tan(deg_to_rad(30.5)),(.5-uv.y)*2.*tan(deg_to_rad(30.5)),-1)).normalized()
			var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(cam.global_position,cam.global_position+ray*65.,1))
			if hit:results[v[0]].append([str(uv),str(hit.position),str(hit.collider.get_parent().name)])
	var heights:=[]
	var sample_path:="res://../../scene_r24/terrace_gardens/probes.json"
	if FileAccess.file_exists(sample_path):
		for q:Array in JSON.parse_string(FileAccess.get_file_as_string(sample_path)):
			var p:=Vector3(q[0],q[1],q[2])
			var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.48,p-Vector3.UP*.60,1))
			heights.append([null,null] if hit.is_empty() else [hit.position.y,str(hit.collider.get_parent().name)])
	FileAccess.open(output.path_join("probe.json"),FileAccess.WRITE).store_string(JSON.stringify({"materials":materials,"views":results,"heights":heights}))
	quit()
