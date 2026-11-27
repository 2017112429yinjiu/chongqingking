extends "../../continuous_site_walk.gd"

const PLAN := "res://assets/district_500/houci-14-16.json"
const FIELD := "res://../../scene_r24/district_refresh/street_groups/houci_14_16/field.json"
const PUBLIC := ["COL_Zhongxing_734116598_Public_Stonewalk", "COL_Panda228_PublicFlagstones"]
var street_maps: Dictionary
var plot: String

func site_plan() -> Dictionary:
	plot = preload("res://scripts/district_500.gd").zhongxing_public_view()
	street_maps = JSON.parse_string(FileAccess.get_file_as_string(FIELD))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var points: Array = plan.public_walks[plot]
	var first: Array = points.front()
	var last: Array = points.back()
	var target: Array = street_maps.plots[plot].center_en
	check("public_route_only", true, {"osm_way":734116598,"exploration_argument":"--zhongxing-public="+plot,"observation_goal":last})
	return {"id":"public_footway_"+plot,"stations":points,"destination_y":last[2],
		"street_focus":[target[0],target[1],last[2]+.65],"return_focus":[first[0],first[1],first[2]+1.63]}

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var report := await super.leg_without_placement(label, goals)
	var confirmed:=0
	var missed:=[]
	for row: Array in walks.back().trace_enu:
		var a:=Vector3(row[0],row[2]+.11,-row[1])
		var ray:=PhysicsRayQueryParameters3D.create(a,a-Vector3.UP*.55,1)
		var contact:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
		var parent_name: String = "" if contact.is_empty() else String(contact.collider.get_parent().name)
		if parent_name in PUBLIC:
			confirmed+=1
		else:
			missed.append({"point":row,"name":parent_name})
	check(label+"_walkway_support",missed.is_empty(),{"samples":confirmed+missed.size(),"public_supports":confirmed,"missed":missed})
	if label.ends_with("_out"):
		var finish: Array = walks.back().finish_enu
		var figure: Dictionary=street_maps.plots[plot]
		var position:=Vector2(finish[0],finish[1])
		var distance:=INF
		var ring: Array=figure.outline_en
		for i in ring.size():
			var from:=Vector2(ring[i][0],ring[i][1])
			var to:=Vector2(ring[(i+1)%ring.size()][0],ring[(i+1)%ring.size()][1])
			var nearest:=Geometry2D.get_closest_point_to_segment(position,from,to)
			distance=minf(distance,position.distance_to(nearest))
		check("old_footprint_observation_distance_"+plot,distance>2.,{"actual_end_enu":finish,
			"old_boundary_m":distance,"old_center_m":position.distance_to(Vector2(figure.center_en[0],figure.center_en[1]))})
	return report

func eye_frame(label: String, focus: Variant) -> void:
	if "--public-look-back-only" in OS.get_cmdline_user_args() and label!="inside_look_back":
		return
	await super.eye_frame(label,focus)
