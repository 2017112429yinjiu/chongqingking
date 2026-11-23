extends "../../scene_r24/day_one/verify.gd"
func support(space:PhysicsDirectSpaceState3D,x:float,z:float,h:Variant)->Array:
	var top:=80. if h==null else float(h)+.38
	var low:=-13. if h==null else float(h)-1.65
	var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,top,z),Vector3(x,low,z),1))
	if hit.is_empty():return [null,""]
	return [snappedf(hit.position.y,.001),str(hit.collider.get_parent().name)]
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(15)
	var space:=scene.get_world_3d().direct_space_state
	var query:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/road_queries.json"))
	var rows:=[];var grid:=[];var absent:=[];var props:=[]
	for row:Array in query.sections:
		var hit:=support(space,row[2],row[3],row[4])
		rows.append(row+hit)
		if hit[0]==null:absent.append(row)
	for pt:Array in query.ground_grid:grid.append(pt+support(space,pt[0],pt[1],pt[2]))
	var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_age/layout.json"))
	var omit:Array[RID]=[]
	for m in scene.find_children("*","MeshInstance3D",true,false):
		if str(m.name).begins_with("COL_Yard20_Bike") or str(m.name).begins_with("COLH_Yard20_Parked"):
			for body in m.get_children():
				if body is StaticBody3D:omit.append(body.get_rid())
	for pt:Array in layout.posts+layout.tyres+layout.pump_feet:
		var p:=Vector3(pt[0],pt[1],pt[2])
		var r:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.18,p-Vector3.UP*.32,1)
		r.exclude=omit
		var contact:=space.intersect_ray(r)
		props.append({"point":pt,"error_m":null if contact.is_empty() else p.y-contact.position.y,"support":"" if contact.is_empty() else str(contact.collider.get_parent().name)})
	var verge:=[]
	for at in range(225,345):
		var x:=float(at)*.1
		var stations:Array=layout.road.south_asphalt_joint
		var near:Array=stations[0]
		for j:Array in stations:
			if absf(x-float(j[0]))<absf(x-float(near[0])):near=j
		var y:float=-near[1]-(x-float(near[0]))*.071
		for k in range(-12,15):
			var z:=y+k*.012
			verge.append([x,z]+support(space,x,z,8.7))
	var median:=[]
	for p:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/median_sections.json")):
		var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],p[2]+1.,p[1]),Vector3(p[0],p[2]-.60,p[1]),1))
		median.append(p+[null,""] if h.is_empty() else p+[h.position.y,str(h.collider.get_parent().name)])
	var median_edge:=[]
	for p:Array in JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/median_open_pixels.json")):
		var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],14.,p[1]),Vector3(p[0],-2.,p[1]),1))
		median_edge.append(p+[null,""] if h.is_empty() else p+[h.position.y,str(h.collider.get_parent().name)])
	var report={"western_extra":median_edge,"western_median":median,"south_joint":verge,"routes":query.routes,"sections":rows,"grid":grid,"void_samples":absent,"contacts":props,"engine":Engine.get_version_info().string,"scene":scene.scene_identity.get("district_connections",{}),"below_another_level":query.probes_below_a_higher_surface,"underground_projection":query.underground_alignment_excluded}
	FileAccess.open(output.path_join("district.json"),FileAccess.WRITE).store_string(JSON.stringify(report))
	quit()
