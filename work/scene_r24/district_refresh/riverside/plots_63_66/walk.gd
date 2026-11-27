extends "../../continuous_site_walk.gd"

const PATH := "res://assets/district_500/changbin-bend-and-edge.json"
const VIEWS := {
	"bend": [
		["bend-west",[-36.10,-155.85,3.99],[-19.3,-155.3,5.75],65.0],
		["bend-east-reverse",[-8.80,-153.40,4.23],[-26.4,-157.4,4.91],67.0],
	],
	"park": [
		["road-and-park-west",[-5.15,-190.54,.27],[12.1,-177.8,1.05],68.0],
		["road-and-park-east", [29.93,-198.65,-3.21],[6.0,-177.2,.8],68.0],
	],
}

var plan: Dictionary
var group: String
var street_way: String
var minimum_road_clearance: float
var before: bool


func site_plan() -> Dictionary:
	var args := OS.get_cmdline_user_args()
	before = "--qa-without-changbin-bend" in args
	group = "bend" if "--changbin-bend" in args else "park"
	street_way = "1256859184" if group == "bend" else "59146737"
	minimum_road_clearance = 5.0 if group == "bend" else 5.12
	plan = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	var site: Dictionary = plan.routes[group]
	var stations: Array = site.stations
	var expected_walk: String = site.walk_mesh
	var preserved := ["COL_Riverside_62_registered_body","COL_Raijiapo_Ramp_1256839997",
		"COL_Raijiapo_GarageParkingSlabs","COL_Park59_PublicPaving","Park61_WestParkEdgePath"]
	check("pavilion_62_garage_bridge_and_park_retained",preserved.all(func(label: String):
		return scene.find_child(label,true,false)!=null),preserved)
	var old_hits := []
	for plot: String in plan.old_plot_centres:
		var label := "COL_Outer500_Frame_" + plot
		var hit_rows := column(plan.old_plot_centres[plot])
		var hit_old := hit_rows.any(func(row: Array):return row[0]==label)
		var node_exists := scene.find_child(label,true,false)!=null
		old_hits.append({"plot":int(plot),"old_frame":node_exists,"old_collision":hit_old,"layers":hit_rows})
	check("old_63_to_66_structure_and_collision",old_hits.all(func(row:Dictionary):
		return row.old_frame==before and row.old_collision==before),old_hits)
	var probes := []
	for location: Array in stations:
		for offset in [-.70,0.,.70]:
			var point := [float(location[0])+.029,location[1]+offset]
			var hits := column(point)
			var walking_slab := hits.filter(func(row: Array):return row[0]==expected_walk and row[2]>.82)
			probes.append({"en":point,"hits":hits,"walk_support":not walking_slab.is_empty(),
				"side_clearance_m":road_clearance(point)})
	var support := probes.all(func(row: Dictionary):
		return (row.side_clearance_m>minimum_road_clearance-.8 and
			(row.walk_support if not before else not row.hits.is_empty())))
	check("three_samples_per_walk_section",support,probes)
	var destination: Array = stations[-1]
	var start: Array = stations[0]
	return {"id":"changbin_"+group,"stations":stations,"destination_y":site.destination_game_m,
		"street_focus":[destination[0],destination[1],site.destination_game_m+1.68],
		"return_focus":[start[0],start[1],site.start_ground_m+1.68]}


func road_clearance(en: Array) -> float:
	var pos := Vector2(en[0],en[1])
	var way: Array = plan.road_axes[street_way]
	var nearest := INF
	var signed_distance := -INF
	for i in range(way.size()-1):
		var p := Vector2(way[i][0],way[i][1])
		var q := Vector2(way[i+1][0],way[i+1][1])
		var foot := Geometry2D.get_closest_point_to_segment(pos,p,q)
		var d := pos.distance_to(foot)
		if d<nearest:
			nearest = d
			var toward_public := pos.y>=foot.y if group=="bend" else pos.y<=foot.y
			signed_distance = d if toward_public else -d
	return signed_distance


func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var movement := await super.leg_without_placement(label,goals)
	var clearance := INF
	for point: Array in walks[-1].trace_enu:
		clearance = minf(clearance,road_clearance(point))
	walks[-1]["minimum_same_side_clearance_m"] = clearance
	walks[-1]["registered_street_way"] = street_way
	check(label+"_clear_of_motor_lane",clearance>minimum_road_clearance,clearance)
	return movement


func eye_frame(label: String, focus: Variant) -> void:
	if label=="street":
		for frame: Array in VIEWS[group]:
			await fixed_view(frame)
	elif label=="inside_look_back":
		await super.eye_frame(label,focus)


func fixed_view(frame: Array) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	var eye: Array = frame[1]
	var target: Array = frame[2]
	camera.position = Vector3(eye[0],eye[2],-eye[1])
	camera.look_at(Vector3(target[0],target[2],-target[1]))
	camera.fov = frame[3]
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var file: String = frame[0]+".png"
	var image := root.get_texture().get_image()
	check("native_"+frame[0],image.save_png(output.path_join(file))==OK,file)
	view_positions.append({"frame":file,"eye_enu":eye,"target_enu":target,
		"vertical_fov_degrees":frame[3],"saved_image_size":str(image.get_size())})
	scene.explorer.camera.make_current()
	camera.queue_free()
