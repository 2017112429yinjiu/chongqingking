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
	for i in range(1,4):
		var frame:=scene.find_child("COL_Court_Jinma_Casework_%d"%i,true,false) as MeshInstance3D
		var finish:=frame.get_active_material(0) as StandardMaterial3D if frame else null
		check("cabinet_grain_contact_%d"%i,finish!=null and finish.albedo_texture!=null and finish.normal_texture!=null and finish.vertex_color_use_as_albedo)
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
			panels.append({"name":label,"contact":bool(mat.get("vertex_color_use_as_albedo")),"pixels":[int(size.x),int(size.y)],"roughness_map":rough!=null or orm!=null})
		check("bound_print_"+key,panels.any(func(v): return v.pixels==[4096,2048] and v.roughness_map),panels)
		check("baked_contact_"+key,panels.all(func(v): return v.contact))
		check("cut_paper_"+key,panels.any(func(v): return v.pixels==[512,1024]))
		if key=="DisplayTables":
			check("printed_open_spread",panels.any(func(v): return v.pixels==[768,512]))
		records.append({"mesh":key,"surfaces":panels})
	FileAccess.open(output.path_join("materials.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"meshes":records},"  "))

func ground(x: float, y: float, h: float) -> Vector3:
	return spot(x,y,h-3.48)

func inspect_floor() -> void:
	var owners := {}
	var high := []
	var unexpected := []
	var missing := 0
	var space := scene.get_world_3d().direct_space_state
	for i in range(1,65):
		for j in range(1,29):
			var pos := ground(i*.5,j*.5,0)
			var ray := PhysicsRayQueryParameters3D.create(pos+Vector3.UP*2.8,pos-Vector3.UP*.12,1)
			var hit := space.intersect_ray(ray)
			if hit.is_empty():
				missing+=1
				continue
			var label := str(hit.collider.get_parent().name)+"/"+str(hit.collider.name)
			owners[label]=owners.get(label,0)+1
			var height: float=hit.position.y-pos.y
			if not label.begins_with("COL_Court_jinma_classrooms/") and not label.begins_with("COL_Court_Structure_jinma_classrooms/"):
				unexpected.append([i*.5,j*.5,snappedf(height,.001),label])
			if height>.045:
				high.append([i*.5,j*.5,snappedf(height,.001),label])
	check("ground_floor_owners",missing==0 and unexpected.is_empty(),{"missing":missing,"unexpected":unexpected.size()})
	FileAccess.open(output.path_join("ground.json"),FileAccess.WRITE).store_string(JSON.stringify({"owners":owners,"raised":high,"unexpected":unexpected,"missing":missing,"checks":checks}))

func inspect_rear(far: float) -> void:
	var rise: float=far-float(room.floor)-.012
	var count:=ceili(rise/.165)
	var axis:=Vector3(room.inward[0],0,-float(room.inward[1]))
	var side:=Vector3(axis.z,0,-axis.x)
	var origin:=Vector3(room.back[0],room.floor+.012,-float(room.back[1]))
	var failed: Array=[]
	var space:=scene.get_world_3d().direct_space_state
	for i in count:
		var along:=.54+(i+.5)*(6.2-.54)/count
		for w: float in [-.96,-.5,0.,.5,.96]:
			var target:=origin+along*axis+w*side+Vector3.UP*rise*(i+1)/count
			var ray:=PhysicsRayQueryParameters3D.create(target+Vector3.UP*2.0,target-Vector3.UP*.3,1)
			var hit:=space.intersect_ray(ray)
			if hit.is_empty() or hit.collider.get_parent().name!=&"COL_Court_FlagstoneApproaches" or absf(hit.position.y-target.y)>.018:
				failed.append([i,w,str(hit.get("position")),str(hit.collider.get_parent().name) if not hit.is_empty() else "missing"])
	check("rear_tread_support",failed.is_empty(),{"treads":count,"probes":count*5,"failed":failed})
	FileAccess.open(output.path_join("rear_steps.json"),FileAccess.WRITE).store_string(JSON.stringify(checks.back(),"  "))

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(32)
	scene.hud.hide()
	check_materials()
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	room=data.buildings.filter(func(r):return r.id=="jinma_classrooms")[0]
	var ring: PackedVector2Array=[]
	for q: Array in room.ring: ring.append(Vector2(q[0],q[1]))
	span=ring[0].distance_to(ring[1])
	depth=(ring[0].distance_to(ring[3])+ring[1].distance_to(ring[2]))*.5
	inspect_floor()
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	inspect_rear(layout.jinma_rear_landing_m)
	if DisplayServer.get_name()=="headless":
		quit(2 if ever_failed else 0)
		return
	await shot("entry",ground(span*.50,.85,1.60),ground(span*.48,depth-1,.85))
	await shot("rear_threshold",ground(span*.50,depth-2.4,1.60),ground(span*.50,depth+2.0,.55))
	await shot("west",ground(3,3.1,1.60),ground(span-3,depth*.62,.83))
	await shot("east",ground(span-2.5,depth-2,1.60),ground(4,depth*.41,.87))
	await shot("rear",ground(span*.51,depth-.88,1.60),ground(span*.47,1,.70))
	await shot("reading_aisle",spot(10.7,depth-4.6,1.6),spot(4.8,depth-.72,1.20))
	await shot("player_shelf",spot(5.78,depth-3.03,1.60),spot(5.78,depth-.72,1.46))
	await shot("spines",spot(5.45,depth-1.73,1.50),spot(5.75,depth-.72,1.37))
	await shot("opposing_case",spot(4.7,3.1,1.60),spot(4.4,1.02,1.3))
	await shot("far_case",spot(span-4.3,depth-3.1,1.60),spot(span-4.1,depth-.72,1.44))
	await shot("table",spot(span*.40-.57,depth*.40-1.04,1.60),spot(span*.40,depth*.40,.91))
	await shot("page_edges",spot(span*.40-.86,depth*.40-.50,1.17),spot(span*.40-.66,depth*.40-.07,.9))
	quit(2 if ever_failed else 0)
