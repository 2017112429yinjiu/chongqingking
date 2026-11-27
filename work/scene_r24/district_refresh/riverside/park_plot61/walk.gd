extends "../../continuous_site_walk.gd"

const PLAN := "res://assets/district_500/park-plot61.json"
const BRIDGE := "res://assets/district_500/bridge-park.json"
const OLD := "COL_Outer500_Frame_61"

var plan: Dictionary
var bridge: Dictionary
var before := false

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	bridge = JSON.parse_string(FileAccess.get_file_as_string(BRIDGE))
	before = "--qa-without-park-plot61" in OS.get_cmdline_user_args()
	var visible_old := []
	for node_name: String in plan.retired_objects:
		if scene.find_child(node_name,true,false):
			visible_old.append(node_name)
	check("old_61_nodes",visible_old.size()==(plan.retired_objects.size() if before else 0),visible_old)
	check("preserved_59_and_62",scene.find_child("COL_Park59_PublicPaving",true,false)!=null
		and scene.find_child("COL_Riverside_62_registered_body",true,false)!=null)
	var heights := column(plan.old_center_enu)
	check("old_volume_collision_above_site",heights.any(func(hit: Array) -> bool: return hit[0]==OLD) == before,heights)
	var sections := []
	for point: Array in plan.route_east_north:
		for dn: float in [-.46, 0., .46]:
			var sample := [point[0]+dn,point[1]]
			sections.append({"en":sample,"contacts":column(sample)})
	check("edge_sections_21",sections.size()==21 and (before or sections.all(
		func(row: Dictionary) -> bool: return not row.contacts.is_empty() and row.contacts[0][2]>.88)),sections)
	var start: Array = plan.route_east_north[0]
	var end: Array = plan.route_east_north[-1]
	check("street_start_on_park_side",road_distance(start)>7.0 and road_distance(start)<8.4,
		{"en":start,"distance_to_road_axis":road_distance(start)})
	return {"id":"changbin_street_to_61_park_edge","stations":plan.route_east_north,
		"street_focus":[end[0],end[1],2.06],"destination_y":plan.destination_game_m,
		"return_focus":[start[0],start[1],2.75]}

func road_distance(en: Array) -> float:
	var p := Vector2(en[0],en[1])
	var clearance := INF
	for i in range(bridge.road_axis.size()-1):
		var a := Vector2(bridge.road_axis[i][0],bridge.road_axis[i][1])
		var b := Vector2(bridge.road_axis[i+1][0],bridge.road_axis[i+1][1])
		var closest := Geometry2D.get_closest_point_to_segment(p,a,b)
		if p.distance_to(closest)<absf(clearance):
			clearance=p.distance_to(closest)*signf((p-a).cross(b-a))
	return clearance

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var clearance := INF
	for en: Array in walks[-1].trace_enu:
		clearance = minf(clearance,road_distance(en))
	check(label+"_off_carriageway",clearance>5.8,clearance)
	return result

func eye_frame(label: String, focus: Variant) -> void:
	if label == "street":
		await capture_registered_view(plan.street_view)
	await super.eye_frame(label,focus)

func capture_registered_view(view: Dictionary) -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(view.frame_px[0],view.frame_px[1])
	viewport.world_3d = scene.get_world_3d()
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var camera := Camera3D.new()
	viewport.add_child(camera)
	camera.keep_aspect=Camera3D.KEEP_HEIGHT
	camera.position=Vector3(view.eye_enu[0],view.eye_enu[2],-view.eye_enu[1])
	var yaw := deg_to_rad(float(view.heading_deg))
	var pitch := deg_to_rad(float(view.pitch_deg))
	var direction := Vector3(sin(yaw)*cos(pitch),sin(pitch),-cos(yaw)*cos(pitch))
	camera.look_at(camera.position+direction)
	camera.fov=float(view.vertical_fov_deg)
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var image := viewport.get_texture().get_image()
	var file := "registered-D.png"
	var saved := image.save_png(output.path_join(file))
	check("native_registered_D",saved==OK and image.get_size()==viewport.size,
		{"frame":file,"actual_size":str(image.get_size())})
	view_positions.append({"frame":file,"eye_enu":view.eye_enu,"heading_deg":view.heading_deg,
		"pitch_deg":view.pitch_deg,"vertical_fov_deg":camera.fov,"pixel_size":str(image.get_size())})
	viewport.queue_free()
