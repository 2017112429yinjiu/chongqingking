extends "../../scene_r24/day_one/verify.gd"
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate();root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(10)
	var s:=scene.get_world_3d().direct_space_state;var out:=[]
	for p:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/median_missing.json")):
		var row:=[]
		for dy in [-.18,-.10,-.04,-.015,-.003,0.,.003,.015,.04,.10,.18]:
			var v:=Vector3(p[0],16.,p[1]+dy)
			var h:=s.intersect_ray(PhysicsRayQueryParameters3D.create(v,v-Vector3.UP*22.,1))
			row.append([dy,h.position.y,str(h.collider.get_parent().name)] if h else [dy,null,""])
		out.append([p,row])
	FileAccess.open(output.path_join("cracks.json"),FileAccess.WRITE).store_string(JSON.stringify(out));quit()
