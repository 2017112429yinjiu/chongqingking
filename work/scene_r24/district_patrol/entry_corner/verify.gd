extends "../../../scene_r24/day_one/verify.gd"

func ground(space:PhysicsDirectSpaceState3D, p:Vector2,h:float=11.)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p.x,h+2.,-p.y),Vector3(p.x,h-2.,-p.y),1))

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	await frames(25)
	RenderingServer.render_loop_enabled=false
	var walker:CharacterBody3D=lesson.demo.walker
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_patrol/measurements.json"))
	var profiles:=[]
	for site:String in source.walk_junctions:
		var rec:Dictionary=source.walk_junctions[site]
		var outline:=PackedVector2Array()
		for point:Array in rec.outline:outline.append(Vector2(point[0],point[1]))
		var box:Array=rec.terrain_bounds
		var missing:=[]
		var old_floor:=[]
		var surface_points:=0
		for x in range(int(box[0])*3,int(box[1])*3):
			for y in range(int(box[2])*3,int(box[3])*3):
				var p:=Vector2(x+.5,y+.5)/3.
				if not Geometry2D.is_point_in_polygon(p,outline):continue
				var near_edge:=false
				for edge in outline.size():
					var d:=Geometry2D.get_closest_point_to_segment(p,outline[edge],outline[(edge+1)%outline.size()])
					if d.distance_to(p)<.10:near_edge=true;break
				if near_edge:continue
				surface_points+=1
				var hit:=ground(space,p,(rec.mouth_heights[0]+rec.mouth_heights[1])*.5)
				if hit.is_empty():
					missing.append(str(p))
					continue
				var part:=str(hit.collider.get_parent().name)
				if part.begins_with("COL_Walk_") or part.contains("Footing") or part.contains("Foundation") or part.contains("StoneFlight") or part.contains("BankCut"):
					old_floor.append([str(p),part])
		check("turn_interior_"+site,surface_points>25 and missing.is_empty() and old_floor.is_empty(),{"points":surface_points,"missing":missing,"old_steps_or_beds":old_floor})
		var centers:=PackedVector2Array()
		var axes:=PackedVector2Array()
		for i in 2:
			var gate:Array=rec.portals[i]
			var a:=Vector2(gate[0][0],gate[0][1])
			var b:=Vector2(gate[1][0],gate[1][1])
			var inward:=(b-a).orthogonal().normalized()*(-1. if i==0 else 1.)
			var level:float=rec.mouth_heights[i]
			var heights:=[]
			var max_error:=0.
			for sample in 25:
				var p:=a.lerp(b,(sample+.5)/25.)
				var inside:=ground(space,p+inward*.045,level)
				var outside:=ground(space,p-inward*.045,level)
				if inside.is_empty() or outside.is_empty():
					max_error=INF
					continue
				var change:float=outside.position.y-inside.position.y
				var rise:float=rec.upper_rise if i==1 else 0.
				max_error=maxf(max_error,absf(change-rise))
				heights.append([sample,inside.position.y,outside.position.y,str(inside.collider.get_parent().name),str(outside.collider.get_parent().name)])
			profiles.append({"site":site,"gate":i,"heights":heights})
			check("full_width_%s_%d"%[site,i],heights.size()==25 and max_error<.035,{"max_error":max_error,"samples":heights.size()})
			centers.append((a+b)*.5)
			axes.append(inward)
		for offset:float in [-.42,0.,.42]:
			var way:=PackedVector3Array()
			for i in 2:
				var side:Vector2=axes[i].orthogonal()*(1. if i==0 else -1.)
				var c:Vector2=centers[i]+side*offset
				var path:= [c-axes[i]*1.5,c+axes[i]*.35] if i==0 else [c+axes[i]*.35,c-axes[i]*1.5]
				for p:Vector2 in path:
					var hit:=ground(space,p,rec.mouth_heights[i])
					if not hit.is_empty():way.append(hit.position)
			if not check("walk_ends_%s_%s"%[site,offset],way.size()==4):continue
			if walker.mounted:walker.dismount(way[0]+Vector3.UP*.18,true)
			else:walker.global_position=way[0]+Vector3.UP*.18
			walker.velocity=Vector3.ZERO
			walker.go(PackedVector3Array([way[1],way[2],way[3],way[2],way[1],way[0]]))
			var round_trip:=false
			for tick in 2800:
				await physics_frame
				round_trip=walker.advance(1./60.,true)
				if round_trip:break
			check("both_directions_%s_%s"%[site,offset],round_trip and walker.is_on_floor(),{"waypoints":walker.index})
	var east_misses:=[]
	for row in 24:
		for col in 9:
			var y:float=-44.+row*.25
			var x:float=50.6+(y+44.)*.28+col*.19
			if ground(space,Vector2(x,y),15.4).is_empty():east_misses.append([x,y])
	check("east_stair_outer_edge",east_misses.is_empty(),{"points":216,"missing":east_misses})
	var courses:=[
		[Vector2(16.12,-71.2),Vector2(16.0,-67.8),Vector2(13.8,-65.1),Vector2(10.1,-62.1)],
		[Vector2(21.8,-66.2),Vector2(16.8,-66.1),Vector2(12.4,-65.8),Vector2(9.8,-66.5)],
		[Vector2(14.95,-70.9),Vector2(14.91,-68.0),Vector2(12.7,-65.1),Vector2(9.5,-63.1)],
		[Vector2(17.12,-70.9),Vector2(17.0,-68.0),Vector2(14.3,-63.8),Vector2(11.5,-60.8)]]
	for k in courses.size():
		var path:=PackedVector3Array()
		for p:Vector2 in courses[k]:
			var hit:=ground(space,p)
			if not hit.is_empty(): path.append(hit.position)
		if not check("ground_%d"%k,path.size()==courses[k].size()):continue
		if walker.mounted:walker.dismount(path[0]+Vector3.UP*.18,true)
		else:walker.global_position=path[0]+Vector3.UP*.18
		walker.velocity=Vector3.ZERO
		var both:=path.slice(1)
		for q in range(path.size()-2,-1,-1):both.append(path[q])
		walker.go(both)
		var done:=false
		for tick in 2800:
			await physics_frame
			done=walker.advance(1./60.,true)
			if done:break
		check("mentor_both_ways_%d"%k,done and walker.is_on_floor(),{"waypoints":walker.index})
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.current=true
	camera.fov=64.
	for view:Array in [
		["player",Vector3(13.37051,13.51703,69.61266),Vector3(16.41107,11.10703,66.57211)],
		["from_street",Vector3(17.1,12.11,71.4),Vector3(13.5,10.93,64.8)],
		["from_stairs",Vector3(9.9,12.90,61.7),Vector3(15.95,10.55,67.7)],
		["from_yard",Vector3(20.85,12.34,65.15),Vector3(13.75,10.82,66.00)]]:
		camera.global_position=view[1]
		camera.look_at(view[2])
		await frames(4)
		await capture(view[0])
	FileAccess.open(output.path_join("corner.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"profiles":profiles},"  "))
	quit(2 if ever_failed else 0)
