extends "../../../scene_r24/outer_neighborhood/survey.gd"

var room: Dictionary
var span: float
var depth: float

func spot(x: float,y: float,h: float) -> Vector3:
	var a:=Vector2(room.ring[0][0],room.ring[0][1])
	var b:=Vector2(room.ring[1][0],room.ring[1][1])
	var c:=Vector2(room.ring[2][0],room.ring[2][1])
	var d:=Vector2(room.ring[3][0],room.ring[3][1])
	var en:=a.lerp(b,x/span).lerp(d.lerp(c,x/span),y/depth)
	return Vector3(en.x,room.floor+3.48+h,-en.y)

func check_materials() -> void:
	var records: Array=[]
	for key: String in ["Case_1","Case_2","Case_3","DisplayTables"]:
		var node:=scene.find_child("Court_Jinma_Books_"+key,true,false) as MeshInstance3D
		if not check("mesh_"+key,is_instance_valid(node)):continue
		var panels: Array=[]
		for i in node.mesh.get_surface_count():
			var mat=node.get_active_material(i)
			var image=mat.get("albedo_texture")
			var label: String=mat.resource_name
			var rough: Texture2D=mat.get("roughness_texture")
			var orm: Texture2D=mat.get("orm_texture")
			var size: Vector2=image.get_size() if image else Vector2.ZERO
			panels.append({"name":label,"pixels":[int(size.x),int(size.y)],"roughness_map":rough!=null or orm!=null})
		check("bound_print_"+key,panels.any(func(v): return v.pixels==[4096,2048] and v.roughness_map),panels)
		check("cut_paper_"+key,panels.any(func(v): return v.pixels==[512,1024]))
		if key=="DisplayTables":
			check("printed_open_spread",panels.any(func(v): return v.pixels==[768,512]))
		records.append({"mesh":key,"surfaces":panels})
	FileAccess.open(output.path_join("materials.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"meshes":records},"  "))

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(32)
	scene.hud.hide()
	check_materials()
	if DisplayServer.get_name()=="headless":
		quit(2 if ever_failed else 0)
		return
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	room=data.buildings.filter(func(r):return r.id=="jinma_classrooms")[0]
	var ring: PackedVector2Array=[]
	for q: Array in room.ring: ring.append(Vector2(q[0],q[1]))
	span=ring[0].distance_to(ring[1])
	depth=(ring[0].distance_to(ring[3])+ring[1].distance_to(ring[2]))*.5
	await shot("player_shelf",spot(5.78,depth-3.03,1.60),spot(5.78,depth-.72,1.46))
	await shot("spines",spot(5.45,depth-1.73,1.50),spot(5.75,depth-.72,1.37))
	await shot("opposing_case",spot(4.7,3.1,1.60),spot(4.4,1.02,1.3))
	await shot("far_case",spot(span-4.3,depth-3.1,1.60),spot(span-4.1,depth-.72,1.44))
	await shot("table",spot(span*.40-.57,depth*.40-1.04,1.60),spot(span*.40,depth*.40,.91))
	await shot("page_edges",spot(span*.40-.86,depth*.40-.50,1.17),spot(span*.40-.66,depth*.40-.07,.9))
	quit(2 if ever_failed else 0)
