extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate();root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(4)
	var materials:={}
	for key in ["COL_Yard20_CornerSurface","COL_Road_734116595_0_asphalt","COL_Road_734116595_0_pavement","COL_Terrain_200m_pavement","Yard20_Entry_A04","Yard20_RoofSheets"]:
		var o:MeshInstance3D=scene.find_child(key,true,false)
		if not o or not o.mesh:continue
		var slots:=[]
		for i in o.mesh.get_surface_count():
			var m=o.get_active_material(i)
			slots.append([o.mesh.surface_get_material(i).resource_name,m.shader.resource_path if m is ShaderMaterial else m.resource_name, o.mesh.surface_get_array_len(i)])
		materials[key]=slots
	FileAccess.open(output.path_join("materials.json"),FileAccess.WRITE).store_string(JSON.stringify(materials))
	quit()
