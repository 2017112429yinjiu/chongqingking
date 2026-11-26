extends "../../scene_r24/street_blocks/views.gd"

func level_point(xy: Array, height: float) -> Vector3:
	return Vector3(xy[0], height + .05, -xy[1])

func apron_point(school: Dictionary, x: float, y: float) -> Vector3:
	var a:=Vector2(school.ring[0][0],school.ring[0][1])
	var b:=Vector2(school.ring[1][0],school.ring[1][1])
	var along:=(b-a).normalized()
	var out:=Vector2(along.y,-along.x)
	var xy:=a+along*x+out*y
	var from:=Vector3(xy.x,school.floor+2,-xy.y)
	var query:=PhysicsRayQueryParameters3D.create(from,from-Vector3.UP*6.,1)
	var hit:=scene.get_world_3d().direct_space_state.intersect_ray(query)
	check("apron_ground_%.2f_%.2f"%[x,y],not hit.is_empty() and hit.collider.get_parent().name==&"COL_Court_Jinma_Apron",str(hit.get("position")))
	return hit.get("position",from)+Vector3.UP*.045

# These two former display walls were part of the structural collision mesh.
# Cross their footprints clear of the stair, including the height of the old frames.
func check_exhibit_crossings(school: Dictionary) -> void:
	var ring:=PackedVector3Array()
	for p: Array in school.ring:
		ring.append(level_point(p,school.floor))
	var along:=(ring[1]-ring[0]).normalized()
	var space:=scene.get_world_3d().direct_space_state
	for bay: int in [2,10]:
		var near:=ring[0].lerp(ring[1],bay/13.0)
		var far:=ring[3].lerp(ring[2],bay/13.0)
		var obstructions: Array=[]
		for depth_fraction: float in [.395,.425,.45]:
			for height: float in [.35,1.45,2.15]:
				var p:=near.lerp(far,depth_fraction)+Vector3.UP*height
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p-along*.7,p+along*.7,1))
				if not hit.is_empty():
					obstructions.append(str(hit.collider.get_parent().name))
		check("former_display_clear_%d"%bay,obstructions.is_empty(),{"rays":9,"blocked":obstructions})
		var mid:=near.lerp(far,.425)
		await trial("former_display_%d"%bay,[mid-along*1.25,mid+along*1.25])

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	var buildings: Dictionary = {}
	for building: Dictionary in data.buildings:
		buildings[building.id] = building
		var shell := scene.find_child("COL_Court_" + str(building.id), true, false)
		check(building.id+"_collisions", shell != null and not shell.find_children("*","StaticBody3D",true,false).is_empty())
	var rooms: Dictionary = {"renai":buildings.renai_long, "school":buildings.jinma_classrooms}
	for key: String in rooms:
		var rec: Dictionary = rooms[key]
		var pts: Array = []
		for q: Array in data.courtyard_connections[key]:
			pts.append(level_point([q[0],q[1]],q[2]))
		pts.append(level_point(rec.inside,rec.floor))
		if key=="renai":
			var crossing: Dictionary=buildings.renai_cross
			pts.append(level_point(rec.joint_inside,rec.floor))
			pts.append(level_point(rec.joint,rec.floor))
			pts.append(level_point(crossing.joint_inside,crossing.floor))
			pts.append(level_point(crossing.inside,crossing.floor))
		else:
			var back := level_point(rec.back,rec.floor)
			pts.append(back-Vector3(rec.inward[0],0,-float(rec.inward[1]))*.6)
			for j in range(data.courtyard_connections.school_back.size()-1,-1,-1):
				var step: Array=data.courtyard_connections.school_back[j]
				pts.append(level_point([step[0],step[1]],step[2]))
		await trial(key+"_from_delivery_court",pts)
	var school: Dictionary=buildings.jinma_classrooms
	await check_exhibit_crossings(school)
	var upper: Array=[level_point(school.inside,school.floor)]
	for step: Array in school.stairs_to_library:
		upper.append(level_point([step[0],step[1]],step[2]))
	await trial("reading_room_stair",upper)
	var across: Array=[]
	for x: float in [2.1,10.1,16.35,24.,30.4]:
		across.append(apron_point(school,x,1.14))
	await trial("walk_beside_school_windows",across)
	var outside: Array=[]
	for x: float in [30.5,25.8,16.8,9.1,2.1]:
		outside.append(apron_point(school,x,5.10))
	await trial("walk_outside_tree_wells",outside)
	var outer: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var old_trunks:=scene.find_child("OuterDistrictTreeTrunks",true,false)
	for xy: Array in data.superseded_outer_roots:
		var index: int=outer.planting.find_custom(func(p: Dictionary):
			return Vector2(p.east_north_up[0],p.east_north_up[1]).distance_to(Vector2(xy[0],xy[1]))<.10)
		if index<0:
			continue
		var old:=scene.find_child("Outer500_Plant_%03d"%index,true,false) as MeshInstance3D
		var overlaps:=old_trunks.get_children().filter(func(shape: Node3D):
			return Vector2(shape.global_position.x,-shape.global_position.z).distance_to(Vector2(xy[0],xy[1]))<.15)
		check("replaced_parent_tree_"+str(index),is_instance_valid(old) and not old.visible and overlaps.is_empty())
	for name: String in ["COLH_Court_Jinma_Trunks","COLH_Court_Jinma_Seating","COLH_Court_Jinma_PlanterBases"]:
		var proxy:=scene.find_child(name,true,false) as MeshInstance3D
		check(name+"_solid",is_instance_valid(proxy) and not proxy.visible and proxy.get_node_or_null("CQ_StaticCollision")!=null)
	var fs:=FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE)
	fs.store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
