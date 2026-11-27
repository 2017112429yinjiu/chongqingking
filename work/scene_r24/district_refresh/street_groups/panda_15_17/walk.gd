extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/panda-15-17.json"
const VIEWS := "res://../../scene_r24/district_refresh/street_groups/panda_15_17/views.json"
const VISUAL_DETAILS := "res://../../scene_r24/district_refresh/street_groups/panda_15_17/visual-detail-views.json"
const PAVING := &"COL_Panda228_PublicFlagstones"

var plot := "15"
var legacy := false

func site_plan() -> Dictionary:
	var registered: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	plot = "17" if "--panda-17" in OS.get_cmdline_user_args() else "15"
	legacy = "--qa-without-panda-frontage" in OS.get_cmdline_user_args()
	check("both_context_frontages_present",scene.find_child("HouciStreet77",true,false)!=null and
		scene.find_child("COL_Guoco_T1_1374780314",true,false)!=null)
	for mesh: String in registered.retired_objects:
		check("previous_"+mesh,(scene.find_child(mesh,true,false)!=null)==legacy)
	var trees_supported := 0
	for specification: Dictionary in registered.trees:
		var mesh := scene.find_child(specification.name,true,false) as MeshInstance3D
		var donor := scene.find_child(specification.donor,true,false) as MeshInstance3D
		if mesh!=null and donor!=null and mesh.mesh==donor.mesh:
			trees_supported+=1
	check("shared_street_trees",trees_supported==(0 if legacy else registered.trees.size()), trees_supported)
	for specification: Dictionary in registered.get("upright_trees",[]):
		var crown := scene.find_child(specification.name,true,false) as MeshInstance3D
		var anchored := crown!=null and crown.global_position.distance_to(Vector3(specification.enu[0],specification.enu[2],-specification.enu[1]))<.015
		check("upright_"+specification.name,(crown==null) if legacy else anchored)
	var sections := []
	var supported := 0
	for transect: Array in registered.minor_cross_sections:
		var contacts := []
		for sample: Array in transect:
			var layers := column(sample)
			var solid := layers.any(func(hit: Array) -> bool: return hit[0]==PAVING and hit[2]>.94)
			supported+=int(solid)
			contacts.append({"enu":sample,"layers":layers,"paving":solid})
		sections.append(contacts)
	check("eight_walkway_cross_sections",legacy or supported==48,{"count":supported,"sections":sections})
	var route: Dictionary=registered.route[plot]
	if not legacy and plot=="15":
		var xy: Array=route.stations[-1]
		var floor := Vector3(xy[0],route.destination_y,-xy[1])
		var ray := PhysicsRayQueryParameters3D.create(floor+Vector3.UP*.14,floor+Vector3.UP*5.4,1)
		var contact := scene.get_world_3d().direct_space_state.intersect_ray(ray)
		var clearance := 5.4 if contact.is_empty() else float(contact.position.y)-floor.y
		check("portal_clear_height",clearance>=2.15,{"vertical_clearance_m":clearance})
	return {"id":"panda_public_"+plot,"stations":route.stations,"destination_y":route.destination_y,
		"street_focus":route.street_focus,"return_focus":route.return_focus}

func eye_frame(label: String, focus: Variant) -> void:
	if label=="inside_look_back":
		await super.eye_frame(label,focus)
		return
	if label!="street":
		return
	var camera := Camera3D.new()
	# The walking body belongs only in its actual first-person view.
	camera.cull_mask &= ~int(scene.explorer.FIRST_PERSON_BODY_LAYER)
	scene.add_child(camera)
	var views: Array=JSON.parse_string(FileAccess.get_file_as_string(VIEWS))
	if "--panda-visual-details" in OS.get_cmdline_user_args():
		var detail_views: Array=JSON.parse_string(FileAccess.get_file_as_string(VISUAL_DETAILS))
		views=detail_views+views
	for view: Dictionary in views:
		if not String(view.file).begins_with(plot+"-"):continue
		camera.global_position=Vector3(view.eye_enu[0],view.eye_enu[2],-view.eye_enu[1])
		camera.look_at(Vector3(view.target_enu[0],view.target_enu[2],-view.target_enu[1]))
		camera.fov=view.fov_deg
		camera.make_current()
		await process_frame
		RenderingServer.force_draw(false,1./60.)
		check("original_camera_"+view.file,root.get_texture().get_image().save_png(output.path_join(view.file))==OK)
		view_positions.append(view)
	scene.explorer.camera.make_current()
	camera.queue_free()
