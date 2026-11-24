extends "../../scene_r24/day_one/verify.gd"

func floor_hit(space:PhysicsDirectSpaceState3D,point:Vector2,high:float=28.0)->Dictionary:
	var top:=Vector3(point.x,high,point.y)
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(top,Vector3(top.x,19.,top.z),1))

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	await frames(30)
	var walker:CharacterBody3D=lesson.demo.walker
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	for row:Array in [["EastLane",Vector2(39.,-4.65),Vector2(50.5,-4.65),-2.0,-6.75],
			["StationRear",Vector2(24.,-18.5),Vector2(31.,-18.5),-16.5,-23.75]]:
		var key:String=row[0]
		var a:Vector2=row[1]
		var b:Vector2=row[2]
		var bad:=[]
		var sampled:=0
		for j in 11:
			for i in 23:
				var at:=Vector2(lerpf(a.x,b.x,i/22.0),lerpf(row[3],row[4],j/10.0))
				var hit:=floor_hit(space,at)
				if hit.is_empty() or str(hit.collider.get_parent().name)!="COL_Patrol25_"+key:bad.append(str(at))
				sampled+=1
		check("single_walk_floor_"+key,bad.is_empty(),{"points":sampled,"other_surfaces":bad})
		for direction in 2:
			var p:=a
			var q:=b
			if direction==1:
				p=Vector2((a.x+b.x)*.5,row[3]+.65)
				q=Vector2(p.x,row[4]-.65)
			else:
				p.x-=1.10
				q.x+=1.10
			var start:=floor_hit(space,p)
			var finish:=floor_hit(space,q)
			if not check("ends_%s_%d"%[key,direction],not start.is_empty() and not finish.is_empty()):continue
			if walker.mounted:walker.dismount(start.position+Vector3.UP*.20,true)
			else:walker.global_position=start.position+Vector3.UP*.20
			walker.velocity=Vector3.ZERO
			walker.go(PackedVector3Array([finish.position,start.position]))
			var completed:=false
			for tick in 1800:
				await physics_frame
				completed=walker.advance(1./60.,true)
				if completed:break
			check("mentor_round_trip_%s_%d"%[key,direction],completed and walker.is_on_floor(),str(walker.global_position))
	FileAccess.open(output.path_join("pavement.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
