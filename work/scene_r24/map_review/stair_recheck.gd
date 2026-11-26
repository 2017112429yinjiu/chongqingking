extends "../../scene_r24/outer_neighborhood/survey.gd"

func foot(p:Dictionary,u:float,v:float) -> Vector3:
	var q:=world(p,u,v,0)
	return public_floor([q.x,-q.z],p.height)

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(24)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var raw:Array=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_DIRECT")))
	var failed:={}
	for row:Dictionary in raw:
		if not row["pass"]:failed[int(str(row.name).split("_")[1])]=true
	for p:Dictionary in data.plots:
		var id:=int(p.plot_id)
		if not failed.has(id):continue
		var f:float=-p.depth*.5
		var routes:Dictionary={}
		if p.has("repair_court"):
			var r:Dictionary=p.repair_court
			var path:=[]
			for k:String in ["street","porch","service"]:
				var q:Array=r[k]
				path.append(Vector3(q[0],q[2]+.045,-q[1]))
			routes["registered"]=path
		elif str(p.name)!="":
			for side:float in [-.27,.22]:
				var u:float=p.width*side
				routes["left" if side<0 else "right"]=[foot(p,u,f-2.35-6.65),world(p,u,f-2.20,.06),world(p,u,f-.55,.06),world(p,p.door_u,f+.72,.06)]
				routes["landing_left" if side<0 else "landing_right"]=[foot(p,u,f-2.35-6.65),
					world(p,u,f-1.42,.06),world(p,p.door_u,f-1.42,.06),world(p,p.door_u,f+.72,.06)]
		elif p.get("kerb_stairs",{}).has("front"):
			var stair:Dictionary=p.kerb_stairs.front
			routes["side"]=[foot(p,stair.toe[0]+stair.direction*.34,stair.toe[1]),world(p,stair.pad[0],stair.pad[1],.06),world(p,p.door_u,f+.72,.06)]
		else:
			for off:float in [-.52,0.,.52]:
				routes["front_%d"%roundi(off*100)]=[foot(p,p.door_u+off,f-float(p.front_stair_m)-.55),
					world(p,p.door_u+off,f-.55,.06),world(p,p.door_u,f+.72,.06)]
		for label:String in routes:
			var route:Array=routes[label]
			for phase:String in ["in","out"]:
				var name:="stair_%02d_%s_%s"%[id,label,phase]
				if route.has(Vector3.INF):check(name,false,{"reason":"toe support missing"})
				else:
					scene.explorer.begin_route_test(route[0],route[-1])
					await frames(20)
					var result:=await WalkTest._walk(scene,route.slice(1),name)
					check(name,result["pass"],result)
				route.reverse()
	FileAccess.open(output.path_join("stairs.json"),FileAccess.WRITE).store_string(JSON.stringify(checks))
	quit(2 if ever_failed else 0)
