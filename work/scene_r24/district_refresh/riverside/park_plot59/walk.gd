extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/park-plot59.json"
const BRIDGE := "res://assets/district_500/bridge-park.json"
const FLOOR := "COL_Park59_PublicPaving"
const OLD := "COL_Outer500_Frame_59"
var plan: Dictionary
var bridge: Dictionary
var before := false

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	bridge = JSON.parse_string(FileAccess.get_file_as_string(BRIDGE))
	before = "--qa-without-park-plot59" in OS.get_cmdline_user_args()
	var present := []
	for name: String in plan.retired_objects:
		if scene.find_child(name,true,false) != null:
			present.append(name)
	check("old_59_and_attached_objects",present.size()==(plan.retired_objects.size() if before else 0),present)
	check("independent_61_in_its_active_version",
		scene.find_child("COL_Outer500_Frame_61",true,false)!=null
		or scene.find_child("Park61_WestParkEdgePath",true,false)!=null)
	check("bridge_and_pavilion_still_present",
		scene.find_child("COL_Nanjimen_NorthRailSteelBox",true,false)!=null
		and scene.find_child("COL_Riverside_62_registered_body",true,false)!=null)

	var center := column([-71.7452,-191.8556])
	var names := center.map(func(hit: Array) -> String: return hit[0])
	check("old_footprint_roof_or_open_paving",
		names.has(OLD) and not names.has(FLOOR) if before else not names.has(OLD) and names.has(FLOOR),
		center)
	var sections := []
	for center_en: Array in plan.sections:
		var section := []
		for offset: float in [-.64,0.,.64]:
			var sample := [center_en[0]+offset,center_en[1]]
			section.append({"en":sample,"hits":column(sample)})
		sections.append(section)
	if not before:
		check("24_actual_paving_and_ground_contacts",sections.size()==8 and sections.all(
			func(section: Array) -> bool: return section.all(func(sample: Dictionary) -> bool:
				return not sample.hits.is_empty() and sample.hits[0][2]>.91)),sections)
	else:
		check("old_contact_profiles",sections.size()==8,sections)
	var start: Array = plan.route_east_north[0]
	var p := scene.explorer.body.global_position as Vector3
	var start_layers := column(start)
	var road_clear := road_distance([p.x,-p.z])
	check("street_start_along_registered_59146737",road_clear>6.5 and road_clear<8.5,
		{"distance_to_road_axis_m":road_clear,"street_enu":enu(p),"floor":start_layers})
	return {"id":"changbin_street_into_park_59","stations":plan.route_east_north,
		"street_focus":[-72.65,-191.0,1.04],
		"destination_y":plan.destination_game_m,"return_focus":[start[0],start[1],p.y+1.19]}

func road_distance(at: Array) -> float:
	var point := Vector2(at[0],at[1])
	var best := INF
	for i in range(bridge.road_axis.size()-1):
		var a := Vector2(bridge.road_axis[i][0],bridge.road_axis[i][1])
		var b := Vector2(bridge.road_axis[i+1][0],bridge.road_axis[i+1][1])
		var n := Geometry2D.get_closest_point_to_segment(point,a,b)
		if point.distance_to(n)<absf(best):
			best=point.distance_to(n)*signf((point-a).cross(b-a))
	return best

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var nearest := INF
	for current: Array in walks[-1].trace_enu:
		nearest=minf(nearest,road_distance(current))
	check(label+"_off_carriageway",nearest>5.70,nearest)
	return result

func eye_frame(label: String, focus: Variant) -> void:
	var close_only := label == "street" and "--roadside-pair-only" in OS.get_cmdline_user_args()
	if not close_only:
		await super.eye_frame(label,focus)
		if label != "street":
			return
		var view: Dictionary = plan.registered_view
		await fixed_view("registered-street-59",view.eye_enu,view.target_enu,view.fov_deg)
	await fixed_view("park-from-roadside",[-77.45,-181.10,2.22],[-71.75,-191.86,1.19],67.)

func fixed_view(label: String, eye: Array, target: Array, fov: float) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.position=Vector3(eye[0],eye[2],-eye[1])
	camera.look_at(Vector3(target[0],target[2],-target[1]))
	camera.fov=fov
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var file := label+".png"
	var saved := root.get_texture().get_image().save_png(output.path_join(file))
	check("native_"+label,saved==OK,file)
	view_positions.append({"frame":file,"eye_enu":eye,"target_enu":target,
		"fov_deg":fov,"pixel_size":str(root.size)})
	scene.explorer.camera.make_current()
	camera.queue_free()
