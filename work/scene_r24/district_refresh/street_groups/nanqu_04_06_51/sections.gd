extends "res://../../scene_r24/day_one/verify.gd"

const DECK := "COL_R24_LinkDeck_R24_link_asphalt"
const WALK := "COL_Nanqu_RiverFootway"
const FLYOVER := "COL_R24_FlyoverBox_R24_link_concrete"
const APPROACH := "COL_Nanqu_RaisedWestApproach"

func enu(row: Array) -> Vector3:
	return Vector3(row[0],row[2],-row[1])

func contact(start: Vector3, finish: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(start,finish,1)
	query.hit_back_faces = false
	var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {}
	return {"body":String(hit.collider.get_parent().name),"y":hit.position.y,"normal_y":hit.normal.y}

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/nanqu-04-06-51.json"))
	var rows: Array=plan.bike_path
	var cross_sections := []
	var under := []
	for i in range(1,rows.size()-1):
		var center := enu(rows[i])
		var direction := enu(rows[i+1])-enu(rows[i-1])
		direction.y=0.
		var normal := direction.normalized().cross(Vector3.UP)
		for delta: float in [-2.65,-1.10,.75]:
			var pt := center+normal*delta
			var surface := contact(pt+Vector3.UP*1.80,pt-Vector3.UP*.17)
			var highest := contact(pt+Vector3.UP*19.,pt-Vector3.UP*.17)
			var matched: bool = surface.get("body","") in [APPROACH,DECK]
			cross_sections.append({"i":i,"x":pt.x,"z":pt.z,"expected_y":pt.y,
				"offset_from_right_lane_m":delta,"support":surface,"above":highest,"pass":matched})
		if i in [7,8,9,11,13,15,17]:
			var beam := contact(center-Vector3.UP*2.28,center-Vector3.UP*.30)
			var below := contact(center-Vector3.UP*1.19,center-Vector3.UP*7.0)
			var clearance := float(beam.get("y",0.))-float(below.get("y",0.))
			var cap: bool = beam.get("body","")=="COL_R24_LinkCaps_R24_link_concrete"
			under.append({"segment":i,"soffit":beam,"ground":below,"clearance_m":clearance,
				"above_test":"pier_cap" if cap else "beam_soffit",
				"pass":(beam.get("body","")==FLYOVER or cap) and not below.is_empty() and clearance>(1.65 if cap else 1.80)})
	var approaches := []
	for row: Array in [[-155.56755,-74.49471,7.628],[-153.66147,-75.20965,7.689]]:
		var base := enu(row)
		var direction := Vector3(.927,0.,.373)
		for offset: float in [-1.5,-.75,0.,.75,1.5]:
			var track := base+direction.cross(Vector3.UP)*offset
			for rise: float in [.08,.24,.49,.90,1.45,2.1]:
				var start := track+Vector3.UP*rise
				var forward := contact(start-direction*1.4,start+direction*1.4)
				var back := contact(start+direction*1.4,start-direction*1.4)
				if not forward.is_empty() or not back.is_empty():
					approaches.append({"enu":row,"offset":offset,"rise":rise,"front":forward,"back":back})
	var pedestrian := []
	for row: Array in plan.public_walk:
		var p := enu(row)
		var found := contact(p+Vector3.UP*1.75,p-Vector3.UP*.08)
		pedestrian.append({"point_enu":row,"surface":found,"pass":found.get("body","")==WALK})
	check("all_wheel_stripes_on_link",cross_sections.all(func(s: Dictionary) -> bool: return s.pass),
		{"count":cross_sections.size()})
	check("bridge_soffit_clear_of_ground",under.all(func(s: Dictionary) -> bool: return s.pass),under)
	check("pedestrian_surface",pedestrian.all(func(s: Dictionary) -> bool: return s.pass),pedestrian)
	FileAccess.open(output.path_join("sections.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"wheel_stripes":cross_sections,"soffit":under,
		"pedestrian":pedestrian,"stall_rays":approaches,"checks":checks,"identity":scene.scene_identity.district_500},"  "))
	quit(2 if ever_failed else 0)
