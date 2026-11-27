extends "../../continuous_site_walk.gd"

const PLAN := "res://assets/district_500/park-plot57.json"
const SEAL := "COL_Park57_NorthDeckWallSeal"
const PAVILION := "res://assets/district_500/pavilion62.json"

var plan: Dictionary
var old_layer := false

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	old_layer = "--qa-without-park-plot57" in OS.get_cmdline_user_args()
	var retired_nodes := []
	for label: String in plan.retired_objects:
		var obj := scene.find_child(label,true,false)
		if obj:
			retired_nodes.append({"name":label,
				"static_bodies":obj.find_children("*","StaticBody3D",true,false).size()})
	check("old_plot_57_instances_" + ("present" if old_layer else "retired"),
		retired_nodes.size()==(plan.retired_objects.size() if old_layer else 0),retired_nodes)
	var plot_probe := column([-121.98,-177.79])
	var old_footprint := plot_probe.any(func(hit: Array) -> bool:
		return hit[0] in ["COL_Outer500_Building_envelopes","COL_Outer500_Frame_57"])
	check("former_57_collider_" + ("observed" if old_layer else "cleared"),
		old_footprint==old_layer,plot_probe)
	var pavilion: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PAVILION))
	check("independent_plot_62_pavilion_retained",pavilion.new_meshes.all(
		func(label: String) -> bool: return scene.find_child(label,true,false)!=null),pavilion.new_meshes)
	var a := en_point(plan.seal_from_east_north_up)
	var b := en_point(plan.seal_to_east_north_up)
	var edge := (a+b)*.5
	var samples := []
	for y in [-5.62,-5.30,-5.0,-4.71,-4.41]:
		var from := Vector3(edge.x,y,edge.z+.42)
		var to := Vector3(edge.x,y,edge.z-.40)
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(
			PhysicsRayQueryParameters3D.create(from,to,1))
		samples.append({"height_m":y,"object":String(hit.collider.get_parent().name) if not hit.is_empty() else ""})
	check("five_closed_seam_ray_heights" if not old_layer else "before_open_seam",
		samples.all(func(hit: Dictionary) -> bool: return hit.object==("" if old_layer else SEAL)),samples)
	if not old_layer:
		check_approach()
		check_neighbor_layers()
	var street_spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(
		"res://assets/district_500/west-ramp.json")).playground.street_access
	return {"id":"riverside_street_to_plot57","stations":plan.route_east_north,
		"street_focus":street_spec.street_focus_east_north_up,"destination_y":plan.destination_y,
		"return_focus":[-140.17,-183.70,-4.42]}

func check_approach() -> void:
	var samples := []
	for station: Array in plan.approach_sections_east_north:
		for dn in [-.83,0.,.83]:
			var point := [station[0],station[1]+dn]
			var ground := column(point).filter(func(hit: Array) -> bool:
				return hit[0] in ["COL_Park57_EastWalkGrade","COL_Outer500_WestCourt_Paving"] 					or String(hit[0]).begins_with("COL_Outer500_Surface_"))
			samples.append({"point":point,"ground":ground[0] if not ground.is_empty() else []})
	check("east_walk_full_width_support",samples.all(func(probe: Dictionary) -> bool:
		return not probe.ground.is_empty() and probe.ground[2]>.89),samples)
	var previous := -5.83
	for point: Dictionary in samples:
		if point.ground.is_empty():
			continue
		check("section_no_unexpected_step",absf(point.ground[1]-previous)<.49,point)
		previous=point.ground[1]

func check_neighbor_layers() -> void:
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var lot_profiles := []
	for lot: Dictionary in layout.plots:
		var id := int(lot.plot_id)
		if id < 58 or id > 61:
			continue
		var en: Array=lot.east_north
		var frame_name := "COL_Outer500_Frame_%02d" % id
		lot_profiles.append({"plot":id,"frame_present":scene.find_child(frame_name,true,false)!=null,
			"centre":column(en),"east_side":column([en[0]+2.,en[1]]),"west_side":column([en[0]-2.,en[1]])})
	check("neighboring_trial_lots_still_present",lot_profiles.size()==4 and
		lot_profiles.all(func(row: Dictionary) -> bool: return row.frame_present),lot_profiles)

func eye_frame(label: String, focus: Variant) -> void:
	await super.eye_frame(label,focus)
	if label != "street":
		return
	var registered: Dictionary = plan.plot57_view
	await native_view("plot57_same_eye",en_point(registered.eye_east_north_up),
		en_point(registered.target_east_north_up),registered.fov_deg)
	for frame: String in plan.defect_cameras:
		var view: Dictionary=plan.defect_cameras[frame]
		var eye := en_point(view.eye_enu)
		var target: Vector3
		if view.has("target_enu"):
			target = en_point(view.target_enu)
		else:
			var coordinates: PackedStringArray=String(view.direction_xyz).trim_prefix("(").trim_suffix(")").split(",")
			target = eye+Vector3(coordinates[0].to_float(),coordinates[1].to_float(),coordinates[2].to_float())
		await native_view("registered_"+frame,eye,target,view.fixed_fov_deg)

func native_view(label: String, eye: Vector3, target: Vector3, fov: float) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.position=eye
	camera.look_at(target)
	camera.fov=fov
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var name := label+".png"
	var result := root.get_texture().get_image().save_png(output.path_join(name))
	check("native_"+label,result==OK,name)
	view_positions.append({"frame":name,"eye_enu":enu(eye),"target_enu":enu(target),
		"fov_deg":fov,"pixel_size":str(root.size)})
	scene.explorer.camera.make_current()
	camera.queue_free()

func en_point(enu_coords: Array) -> Vector3:
	return Vector3(enu_coords[0],enu_coords[2],-enu_coords[1])
