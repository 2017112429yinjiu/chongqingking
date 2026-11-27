extends "../../continuous_site_walk.gd"

const MODEL := "res://assets/district_500/raijiapo-east-bend.json"
const CAMERAS := [
	["bend-east-reverse",[-8.80,-153.40,4.23],[-26.4,-157.4,4.91],67.0],
	["road-and-park-west",[-5.15,-190.54,.27],[12.1,-177.8,1.05],68.0],
	["east-side-street-entry",[37.0,-162.15,.65],[48.55,-159.95,.70],67.0],
	["east-road-markings-eye",[49.8,-163.02,1.21],[21.,-179.6,-1.0],68.0],
]

var source: Dictionary
var before: bool

func site_plan() -> Dictionary:
	before = "--qa-without-raijiapo-east" in OS.get_cmdline_user_args()
	source = JSON.parse_string(FileAccess.get_file_as_string(MODEL))
	var rows := []
	for key: String in source.old_centres:
		var label := "COL_Outer500_Frame_"+key
		var hits := column(source.old_centres[key])
		rows.append({"plot":key,"layers":hits,"has_legacy_node":scene.find_child(label,true,false)!=null,
			"legacy_collision":hits.any(func(row: Array):return row[0]==label)})
	check("tested_old_frames_and_collisions",rows.all(func(row: Dictionary):
		return row.has_legacy_node==before and row.legacy_collision==before),rows)
	var plot70 := "COL_Binjiang_1128648941_Podium" if scene.find_child("BinjiangFrontages",true,false) else "COL_Outer500_Frame_70"
	var names := [plot70,"COL_Riverside_62_registered_body",
		"COL_Changbin_GarageSideWalk","COL_Changbin_ParkSideWalk","COL_Raijiapo_GaragePublicEnvelope"]
	check("previous_walks_pavilion_and_next_district",names.all(func(label: String):
		return scene.find_child(label,true,false)!=null),names)
	var paint_names := ["EastRoad_GroundPaint_59146737","EastRoad_Lines_1324001436",
		"EastRoad_Lines_1375242615","EastRoad_Lines_1375242617"]
	check("same_model_surface_and_marking_objects",paint_names.all(func(label: String):
		return (scene.find_child(label,true,false)!=null)!=before),paint_names)
	if not before:
		var borrowed := []
		for label: String in source.borrowed_materials:
			var node := scene.find_child(label,true,false) as MeshInstance3D
			for index in node.mesh.get_surface_count():
				var finish := node.mesh.surface_get_material(index)
				if String(finish.resource_name).begins_with("CQEastParentSlot"):
					borrowed.append([label,index,finish.resource_name])
		check("parent_material_resources_restored",borrowed.is_empty(),borrowed)
	var walk: Dictionary = source.walk
	var stations: Array = walk.stations
	var samples := []
	for station: Array in stations:
		for step in [-.66,0.,.66]:
			var point := [station[0]+.025,station[1]+step]
			var hits := column(point)
			var foot := hits.any(func(row: Array): return row[0]=="COL_EastRoad_PublicWalk" and row[2]>.84)
			samples.append({"point_enu":point,"layers":hits,"public_footway":foot,
				"centreline_clearance_m":clearance(point)})
	check("public_walk_left_right_and_centre",samples.all(func(row: Dictionary):
		return row.centreline_clearance_m>4.95 and (row.public_footway or before)),samples)
	var first: Array = stations[0]
	return {"id":"raijiapo_east_public_edge","stations":stations,"destination_y":walk.finish_z_m,
		"street_focus":[48.55,-159.95,1.6],"return_focus":[first[0],first[1],.66]}

func clearance(en: Array) -> float:
	var p := Vector2(en[0],en[1])
	var best := INF
	var side := -INF
	for i in range(source.road_axis.size()-1):
		var a: Array=source.road_axis[i]
		var b: Array=source.road_axis[i+1]
		var foot:=Geometry2D.get_closest_point_to_segment(p,Vector2(a[0],a[1]),Vector2(b[0],b[1]))
		var d:=p.distance_to(foot)
		if d<best:
			best=d
			side=d if p.y>=foot.y else -d
	return side

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result:=await super.leg_without_placement(label,goals)
	var gap:=INF
	for row: Array in walks[-1].trace_enu:
		gap=minf(gap,clearance(row))
	walks[-1]["min_1256859184_same_side_m"]=gap
	check(label+"_kept_on_north_side",gap>5.60,gap)
	return result

func eye_frame(label: String, focus: Variant) -> void:
	if label=="street":
		for camera: Array in CAMERAS:
			await fixed_frame(camera)
	elif label=="inside_look_back":
		await super.eye_frame(label,focus)

func fixed_frame(record: Array) -> void:
	var camera:=Camera3D.new()
	scene.add_child(camera)
	var eye: Array=record[1]
	var target: Array=record[2]
	camera.position=Vector3(eye[0],eye[2],-eye[1])
	camera.look_at(Vector3(target[0],target[2],-target[1]))
	camera.fov=record[3]
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var file: String=record[0]+".png"
	var bitmap:=root.get_texture().get_image()
	check("native_"+record[0],bitmap.save_png(output.path_join(file))==OK,file)
	view_positions.append({"frame":file,"eye_enu":eye,"target_enu":target,
		"vertical_fov_degrees":record[3],"saved_image_size":str(bitmap.get_size())})
	scene.explorer.camera.make_current()
	camera.queue_free()
