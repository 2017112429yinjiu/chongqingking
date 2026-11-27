extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/houci-77.json"
const VIEWS := "res://../../scene_r24/district_refresh/street_groups/houci_77/views.json"
const ROAD := "COL_Houci_1306489251_Asphalt"
const WALK := "COL_Houci_Public_Flagstones"
const KERB := "COL_Houci_Street_Kerbs"

var plan: Dictionary
var comparison := false

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	comparison = "--qa-without-houci-77" in OS.get_cmdline_user_args()
	var retained := ["COL_Guoco_T1_1374780314", "COL_Guoco_T2_1374780313",
		"COL_Guoco_PodiumPublicPassage"]
	for name: String in retained:
		check("retained_"+name, scene.find_child(name,true,false)!=null)
	var old := []
	for name: String in plan.retired_objects:
		if scene.find_child(name,true,false)!=null:
			old.append(name)
	check("intended_old_nodes", old.size()==(plan.retired_objects.size() if comparison else 0), old)
	var plot_center := column([208.619,-27.9386])
	check("centre_legacy_roof_collision", plot_center.any(func(hit: Array) -> bool:
		return hit[0]=="COL_Outer500_Frame_77") == comparison, plot_center)

	var profiles := []
	var samples_passed := 0
	var surfaces := [WALK,WALK,KERB,ROAD,ROAD,ROAD,KERB,WALK,WALK]
	for cross: Array in plan.sections_east_north:
		var span := []
		for i in cross.size():
			var layers := column(cross[i])
			var pass_point: bool = not layers.is_empty() and layers[0][0]==surfaces[i] and layers[0][2]>.9
			samples_passed += int(pass_point)
			span.append({"en":cross[i],"expected":surfaces[i],"layers":layers,"pass":pass_point})
		profiles.append(span)
	check("street_cross_sections", comparison or samples_passed==81,
		{"passed":samples_passed,"total":81,"profiles":profiles})
	var start: Array = plan.walk.stations[0]
	var finish: Array = plan.walk.stations[-1]
	return {"id":"houci_77_public_walk","stations":plan.walk.stations,
		"street_focus":[finish[0],finish[1],plan.walk.destination_y+1.30],
		"destination_y":plan.walk.destination_y,
		"return_focus":[start[0],start[1],plan.walk.start_y+1.42]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	if comparison:
		return result
	var clearance := INF
	for sample: Array in walks.back().trace_enu:
		var point := Vector2(sample[0],sample[1])
		for i in plan.road_axis.size()-1:
			var a: Array = plan.road_axis[i]
			var b: Array = plan.road_axis[i+1]
			var closest := Geometry2D.get_closest_point_to_segment(point,Vector2(a[0],a[1]),Vector2(b[0],b[1]))
			clearance = minf(clearance,point.distance_to(closest))
	check(label+"_off_carriageway", clearance>3.78, clearance)
	return result

func eye_frame(label: String, focus: Variant) -> void:
	if label == "street":
		var camera := Camera3D.new()
		scene.add_child(camera)
		var positions: Array = JSON.parse_string(FileAccess.get_file_as_string(VIEWS))
		for frame: Dictionary in positions:
			camera.global_position = Vector3(frame.eye_enu[0],frame.eye_enu[2],-frame.eye_enu[1])
			camera.look_at(Vector3(frame.target_enu[0],frame.target_enu[2],-frame.target_enu[1]))
			camera.fov = frame.fov_deg
			camera.make_current()
			await process_frame
			RenderingServer.force_draw(false,1./60.)
			var saved := root.get_texture().get_image().save_png(output.path_join(frame.file))
			check("fixed_frame_"+frame.file,saved==OK)
			view_positions.append(frame)
		scene.explorer.camera.make_current()
		camera.queue_free()
	elif label == "inside_look_back":
		await super.eye_frame(label,focus)
