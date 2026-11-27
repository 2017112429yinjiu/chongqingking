extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(16)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary={}
	for item: Dictionary in data.plots:
		if int(item.plot_id)==53:
			p=item
			break
	if p.is_empty():
		push_error("Plot 53 is absent from the current layout")
		quit(2)
		return
	var edge:float=p.door_u+1.25
	var end:float=p.depth*.5+p.back_stair_m
	var sections:=[]
	var gaps:=[]
	var largest:=0.0
	for v:float in [end-.75,end-.43,end-.11]:
		var row:=[]
		for j in range(43):
			var u:float=edge-.1+j*.05
			var origin:=world(p,u,v,1)
			var hit:=scene.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,origin-Vector3.UP*12,1))
			if hit.is_empty():
				row.append([u,null,""])
				gaps.append([v,u,"missing ground"])
			else:
				row.append([u,hit.position.y,str(hit.collider.get_parent().name)])
		if row[1][1]!=null and row[3][1]!=null:
			var delta:float=absf(row[1][1]-row[3][1])
			largest=maxf(largest,delta)
			if delta>.025:gaps.append([v,delta])
		sections.append(row)
	if DisplayServer.get_name()!="headless":
		scene.hud.hide()
		await shot("uphill",world(p,edge+2.25,end+.6,-2.10),world(p,edge-.28,end-.37,-2.93))
		await shot("downhill",world(p,edge-.44,end-.76,-1.20),world(p,edge+1.03,end+.12,-3.30))
	var info={"plot":53,"profiles":sections,"max_difference_across_joint_m":largest,"failures":gaps}
	FileAccess.open(output.path_join("landing_profile.json"),FileAccess.WRITE).store_string(JSON.stringify(info,"  "))
	quit(0 if gaps.is_empty() else 2)
