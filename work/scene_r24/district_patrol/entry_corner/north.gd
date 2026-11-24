extends "../../../scene_r24/day_one/verify.gd"

func support(space:PhysicsDirectSpaceState3D, x:float, z:float, reference:float)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,reference+2.,z),Vector3(x,reference-1.65,z),1))

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	await frames(20)
	var survey_path:="ground/district.json"
	var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(output.get_base_dir().path_join(survey_path)))
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	var measurements:=[]
	for category:String in ["sections","grid"]:
		for sample:Array in source[category]:
			if sample[-2]!=null:continue
			var start:=2 if category=="sections" else 0
			var x:float=sample[start]
			var z:float=sample[start+1]
			var ref:float=sample[start+2]
			var record:={"point":[x,z],"old_height":ref,"support":[]}
			var heights:=[]
			for offset:Vector2 in [Vector2.ZERO,Vector2.LEFT,Vector2.RIGHT,Vector2.UP,Vector2.DOWN]:
				var hit:=support(space,x+offset.x*.12,z+offset.y*.12,ref)
				if hit.is_empty():continue
				var label:=str(hit.collider.get_parent().name)
				record.support.append([hit.position.y,label])
				if label.begins_with("COL_Terrain_200m") or label=="COL_Road_734116597_0_pavement":heights.append(hit.position.y)
			var continuous:=heights.size()==5 and float(heights.max())-float(heights.min())<.14
			check("recheck_%s_%d"%[category,measurements.size()],continuous,record)
			measurements.append(record)
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_patrol/measurements.json"))
	var seam:=[]
	for row:Array in build.north_frontage.sidewalk_edge:
		if row[0]<-29.5 or row[0]>-18.5:continue
		var yard:=support(space,row[0],-row[1]+.065,row[2])
		var walk:=support(space,row[0],-row[1]-.065,row[2])
		var ok:=not yard.is_empty() and not walk.is_empty()
		var change:float=absf(walk.position.y-yard.position.y) if ok else INF
		check("north_sidewalk_%d"%seam.size(),ok and change<.05,{"point":row,"difference_m":change})
		seam.append(change)
	var walker:CharacterBody3D=lesson.demo.walker
	var way:=PackedVector3Array()
	for point:Vector3 in [Vector3(-20.1,30.65,-75.2),Vector3(-21.3,31.0,-77.0),Vector3(-23.,31.2,-79.),Vector3(-24.6,31.45,-81.),Vector3(-25.,31.83,-83.)]:
		var hit:=support(space,point.x,point.z,point.y)
		if not hit.is_empty():way.append(hit.position)
	if check("north_walk_ground",way.size()==5):
		if walker.mounted:walker.dismount(way[0]+Vector3.UP*.18,true)
		else:walker.global_position=way[0]+Vector3.UP*.18
		walker.velocity=Vector3.ZERO
		var path:=way.slice(1)
		for k in range(way.size()-2,-1,-1):path.append(way[k])
		walker.go(path)
		var finished:=false
		RenderingServer.render_loop_enabled=false
		for tick in 2200:
			await physics_frame
			finished=walker.advance(1./60.,true)
			if finished:break
		check("north_both_ways",finished and walker.is_on_floor(),{"waypoints":walker.index})
		var camera:=Camera3D.new()
		scene.add_child(camera)
		camera.current=true
		for i in 2:
			camera.global_position=way[0 if i==0 else -1]+Vector3(1.3,1.64,-.2)
			camera.look_at(way[2]+Vector3.UP*.27)
			await frames(4)
			await capture("north_grade_%d"%i)
	FileAccess.open(output.path_join("north.json"),FileAccess.WRITE).store_string(JSON.stringify({"measurements":measurements,"edge_differences_m":seam,"checks":checks},"  "))
	quit(2 if ever_failed else 0)
