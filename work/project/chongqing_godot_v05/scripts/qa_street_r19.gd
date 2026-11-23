extends RefCounted
static func run(main: Node3D) -> void:
	var tests: Array=[]
	var city: Node3D=main.get_node("City")
	var layer: Node3D=city.get_node_or_null("StreetLifeR19")
	var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/street_r19/manifest.json"))
	tests.append({"name":"detail_layer_loaded","pass":layer!=null})
	var missing: Array=[]
	for expected: String in spec.hide_city_objects:
		var match: Node=city.find_child(expected,true,false)
		if match==null or match.visible:missing.append(expected)
	tests.append({"name":"exact_obsolete_geometry_replaced","pass":missing.is_empty(),"missing_or_visible":missing})
	if layer!=null:
		var canopy: MeshInstance3D=layer.find_child("R19_Canvas_awning_cloth",true,false)
		var color_count: int=0
		if canopy!=null:
			for i in range(canopy.mesh.get_surface_count()):
				if canopy.mesh.surface_get_format(i)&Mesh.ARRAY_FORMAT_COLOR:color_count+=1
		tests.append({"name":"imported_canvas_weathering_colors","pass":color_count>0,"colored_surfaces":color_count})
		for prop: Dictionary in spec.grounded_props:
			var name: String="COLH_R19_"+str(prop.name)+"_iron"
			var proxy: MeshInstance3D=layer.find_child(name,true,false)
			var ok: bool=proxy!=null and proxy.has_node("CQ_StaticCollision") and not proxy.visible
			var hit_name: String=""
			if ok:
				var aabb: AABB=proxy.mesh.get_aabb()
				var center: Vector3=proxy.to_global(aabb.get_center())
				var start: Vector3=center+Vector3(aabb.size.x*.5+.16,0,0)
				var query:=PhysicsRayQueryParameters3D.create(start,center,1)
				var hit: Dictionary=main.get_world_3d().direct_space_state.intersect_ray(query)
				if not hit.is_empty():hit_name=str(hit.collider.get_parent().name)
				ok=hit_name==name
			tests.append({"name":"rigid_prop_contact_"+str(prop.name),"pass":ok,"first_hit":hit_name})
		var retained: int=0
		for mesh: Node in layer.find_children("COL_R19_Stair_retaining*","MeshInstance3D",true,false):
			if mesh.has_node("CQ_StaticCollision"):retained+=1
		tests.append({"name":"new_stair_sidewalls_have_collision","pass":retained==2,"bodies":retained})
	var passed: bool=true
	for t: Dictionary in tests:passed=passed and bool(t["pass"])
	var report: Dictionary={"passed":passed,"tests":tests,"scope":"Actual imported detail layer, replacement visibility and physics rays into new rigid props. Full route traversal runs separately."}
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var dir: String=preload("res://scripts/qa_context.gd").directory("res://verification_r19")
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/street_test.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("R19_STREET_QA ",JSON.stringify(report))
	main.get_tree().quit(0 if passed else 2)
