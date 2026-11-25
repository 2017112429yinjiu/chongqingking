extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(24)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
	for house: Dictionary in data.buildings:
		var door:=Vector2(house.door[0],house.door[1])
		var ring: Array=house.wall_base_corners
		var best:=INF
		var inward:=Vector2.ZERO
		var center:=Vector2.ZERO
		for v: Array in ring:center+=Vector2(v[0],v[1])/ring.size()
		for k in ring.size():
			var a:=Vector2(ring[k][0],ring[k][1])
			var b:=Vector2(ring[(k+1)%ring.size()][0],ring[(k+1)%ring.size()][1])
			var d:=Geometry2D.get_closest_point_to_segment(door,a,b).distance_to(door)
			if d>=best:continue
			best=d
			inward=a.direction_to(b).orthogonal()
			if inward.dot(center-door)<0:inward=-inward
		var outside:=door-inward*1.55
		var inside:=door+inward*1.32
		var entry:=terrain([outside.x,outside.y])+Vector3.UP*.045
		await trial("door_"+str(house.osm),[entry,Vector3(door.x,house.floor_z+.045,-door.y),Vector3(inside.x,house.floor_z+.045,-inside.y)])
	FileAccess.open(output.path_join("doors.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
