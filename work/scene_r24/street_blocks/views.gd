extends "../../scene_r24/outer_neighborhood/survey.gd"

func terrain(xy: Array) -> Vector3:
	var a:=Vector3(xy[0],130,-xy[1])
	var ray:=PhysicsRayQueryParameters3D.create(a,a-Vector3.UP*165.,1)
	var omit:Array[RID]=[]
	for i in 80:
		ray.exclude=omit
		var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty(),"Missing terrain at "+str(xy))
		if str(hit.collider.get_parent().name).begins_with("COL_Outer500_Surface_"):return hit.position
		omit.append(hit.rid)
	return Vector3.INF

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for id: int in [3,4,13,41]:
		var arr: Array=layout.plots.filter(func(p):return int(p.plot_id)==id)
		var p: Dictionary=arr[0]
		var f: float=-p.depth*.5
		var eye:=world(p,p.door_u-8.1,f-7.8,0)
		var ground:=public_floor([eye.x,-eye.z],p.height+.2)
		await shot("road_%02d"%id,ground+Vector3.UP*1.58,world(p,p.door_u+.2,f-1.2,.12))
	var geo: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://source_data/geo_layout.json"))
	for path: Dictionary in geo.paths:
		if int(path.id)!=734116601:continue
		for i: int in [4,7,29,34]:
			var foot:=terrain(path.points[i]) if i<10 else public_floor(path.points[i],33)
			var far:=terrain(path.points[i-2]) if i<10 else public_floor(path.points[i-2],33)
			if i==4:far=terrain([-207.,181.])+Vector3.UP*1.35
			if i==7:far=terrain([-228.,160.])+Vector3.UP*1.35
			await shot("path_%02d"%i,foot+Vector3.UP*1.62,far+Vector3.UP*.9)
	quit()
