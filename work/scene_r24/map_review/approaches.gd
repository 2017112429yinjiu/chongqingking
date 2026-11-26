extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(24)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for lane:Dictionary in data.lanes:
		if lane.type!="street":continue
		var p:Dictionary=data.plots[lane.plots[0]]
		var points:Array=[]
		var alignment:Array=lane.points.duplicate()
		alignment.reverse()
		for q:Array in alignment:points.append(public_floor(q,p.height))
		var f:float=-p.depth*.5
		points.append(world(p,p.door_u,f-.55,.06))
		points.append(world(p,p.door_u,f+.72,.06))
		for phase:String in ["in","out"]:
			var name:="street_%02d_%s"%[int(p.plot_id),phase]
			if points.has(Vector3.INF):check(name,false,{"reason":"missing starting support","path_en":alignment})
			else:
				scene.explorer.begin_route_test(points[0],points[-1])
				await frames(20)
				var result:=await WalkTest._walk(scene,points.slice(1),name)
				check(name,result["pass"],result)
			points.reverse()
	FileAccess.open(output.path_join("approaches.json"),FileAccess.WRITE).store_string(JSON.stringify(checks))
	quit(0 if not ever_failed else 2)
