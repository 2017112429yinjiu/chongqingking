extends SceneTree
func _initialize()->void:
	call_deferred("check_rooms")

func segment_distance(node:MeshInstance3D,at:Vector3,dir:Vector3)->float:
	var a:=node.to_local(at-dir*.04)
	var b:=node.to_local(at+dir*.04)
	var vertices:=node.mesh.get_faces()
	var nearest:=INF
	for i in range(0,vertices.size(),3):
		var hit=Geometry3D.segment_intersects_triangle(a,b,vertices[i],vertices[i+1],vertices[i+2])
		if hit!=null:nearest=minf(nearest,node.to_global(hit).distance_to(at))
	return nearest

func check_rooms()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var base=game.get_node("City");var layout=JSON.parse_string(FileAccess.get_file_as_string("res://assets/rooms_r24/layout.json"))
	var fixture_checks=[];var failures=[]
	for row in layout.fixtures:
		var is_floor:bool=row[0]=="Room15_PantryBench"
		var room:String="IR_B_A04_courtyard_home_Interiors_" if is_floor else "IR_B_A01_noodle_Interiors_"
		var original:=base.find_child(room+("room_floor" if is_floor else "room_wall"),true,false) as MeshInstance3D
		var furniture:=base.find_child(row[0],true,false) as MeshInstance3D
		var p=Vector3(row[1][0],row[1][1],row[1][2])
		var dir=Vector3.UP if is_floor or row[0]=="Room15_Pendant" else Vector3.RIGHT
		var fit:=segment_distance(original,p,dir) if original else INF
		var touches:=segment_distance(furniture,p,dir) if furniture else INF
		fixture_checks.append({"part":row[0],"original_m":fit if is_finite(fit) else null,"mounted_m":touches if is_finite(touches) else null})
		if fit>.004 or touches>.015:failures.append(row[0])
	var service=[]
	for row in layout.contacts:
		var urn:=base.find_child(row[0],true,false) as MeshInstance3D
		var support:=base.find_child("Room15_TeaShelf" if row[0]=="Room15_TeaService" else "Room15_PantryBench",true,false) as MeshInstance3D
		var p=Vector3(row[1][0],row[1][1],row[1][2])
		var low:=segment_distance(urn,p,Vector3.UP);var high:=segment_distance(support,p,Vector3.UP)
		service.append({"part":row[0],"bottom_m":low if is_finite(low) else null,"support_m":high if is_finite(high) else null})
		if low>.002 or high>.002:failures.append(row[0])
	var lights=base.find_child("WindowRooms15",true,false).find_children("*","SpotLight3D",true,false)
	for light in lights:
		if light.light_cull_mask!=(1<<15) or not light.distance_fade_enabled or light.shadow_enabled:failures.append("light_mask")
	var stats:Dictionary=game.scene_identity.get("window_rooms",{})
	if lights.size()!=3 or stats.get("existing_room_meshes",0)<5:failures.append("room_install")
	var border_meshes=[]
	if game.art_profile.get("room_patina_r24",false):
		var masks=JSON.parse_string(FileAccess.get_file_as_string("res://assets/rooms_r24/patina.json"))
		for pair in masks.donors:
			var painted:=base.find_child(pair[0],true,false) as MeshInstance3D
			var uv:PackedVector2Array=painted.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV2]
			var valid:=not uv.is_empty() and painted.material_override is ShaderMaterial
			for coord in uv:
				if coord.x<-.001 or coord.y<-.001 or coord.x>1.001 or coord.y>1.001:valid=false
			if not valid:failures.append(pair[0])
			border_meshes.append({"name":pair[0],"UV2":uv.size(),"valid":valid})
		if stats.get("patina_batches",0)!=2:failures.append("coat_install")
	if game.art_profile.get("wall_occlusion_r24", false):
		var walls := base.get_node_or_null("OpaqueFacadeOcclusion") as OccluderInstance3D
		if not root.use_occlusion_culling or not walls or not walls.occluder is ArrayOccluder3D or walls.occluder.get_indices().size() != 8406 * 3:
			failures.append("opaque_facade_geometry")
	var report={"passed":failures.is_empty(),"failures":failures,"fixtures":fixture_checks,"shelf_and_counter":service,"wall_stains":border_meshes}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	var out=preload("res://scripts/qa_context.gd").directory("res://verification_r24/build15")
	DirAccess.make_dir_recursive_absolute(out)
	FileAccess.open(out+"/window_rooms.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("ROOM15_QA ",report.passed," ",failures," ",stats)
	quit(0 if report.passed else 3)
