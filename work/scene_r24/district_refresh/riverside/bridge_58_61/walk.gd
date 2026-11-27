extends "../../continuous_site_walk.gd"

const SITE := "res://assets/district_500/bridge-park.json"
const RAIL := "COL_Nanjimen_NorthRailSteelBox"
const GARAGE := "COL_Raijiapo_GarageParkingSlabs"
const RAMP_WEST := "COL_Raijiapo_Ramp_1256840000"
const RAMP_EAST := "COL_Raijiapo_Ramp_1324001438"

var plan: Dictionary
var baseline := false

func site_plan() -> Dictionary:
	plan = JSON.parse_string(FileAccess.get_file_as_string(SITE))
	baseline = "--qa-without-bridge-park" in OS.get_cmdline_user_args()
	var vacant := []
	for name: String in plan.retired_objects:
		if scene.find_child(name,true,false) == null:
			vacant.append(name)
	check("old_trial_geometry_58_and_60", vacant.size() == (0 if baseline else plan.retired_objects.size()), vacant)
	for id: int in [59,61,62]:
		var name := "COL_Outer500_Frame_%02d" % id
		if id == 62:
			var pavilion: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
				"res://assets/district_500/pavilion62.json"))
			name = pavilion.new_meshes[0]
		check("adjacent_plot_%d" % id, scene.find_child(name,true,false) != null, name)

	for id: String in plan.plots:
		var centre: Array = plan.plots[id]
		var cross_section := []
		for dn in [-.87,0.,.87]:
			var point := [centre[0],centre[1]+dn]
			cross_section.append({"en":point,"contacts":column(point),"ground":ground_contact(point)})
		check("walkable_ground_" + id, cross_section.all(func(p: Dictionary) -> bool:
			return not p.ground.is_empty() and p.ground[2] >= .82), cross_section)

	var rail_floor := ground_contact(plan.plots["58"])
	if not rail_floor.is_empty():
		var position := Vector3(plan.plots["58"][0], rail_floor[1]+1.68, -plan.plots["58"][1])
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(
			PhysicsRayQueryParameters3D.create(position,position+Vector3.UP*58.,1))
		var name := String(hit.collider.get_parent().name) if not hit.is_empty() else ""
		check("rail_above_public_ground", (name == RAIL) != baseline,
			{"mesh":name,"clear_height_from_player_head_m":hit.position.y-position.y if not hit.is_empty() else null})
		if name == RAIL:
			var street_relative := float(hit.position.y) - float(plan.camera_58_street_floor_game_m)
			var core: Array = plan.fitted_pier_bases_and_box_soffits[1]
			var pier := column([core[0],core[1]])
			check("registered_near_road_rail_soffit",
				street_relative >= 40. and street_relative <= 44.
				and layer_names(pier).has("COL_Nanjimen_NorthRailPiers"),
				{"rail_soffit_m_above_street":street_relative,"pier_enu_and_soffit":core,"column":pier})

	for spec: Array in [[58,[-101.196,-154.324]],[60,[-66.319,-163.366]]]:
		var layers := column(spec[1])
		var names := layer_names(layers)
		check("garage_at_superseded_plot_%d" % int(spec[0]), names.has(GARAGE) != baseline, layers)
	if not baseline:
		var garage_trace := []
		for e: float in [-145.,-132.,-116.,-101.,-91.,-79.,-64.,-52.]:
			var sample := roof_at(e)
			var slab := column([e,sample[1]+4.6])
			garage_trace.append({"roof_source":sample,"contacts":slab})
		check("continuous_parking_slabs_behind_facade", garage_trace.all(func(p: Dictionary) -> bool:
			return layer_names(p.contacts).has(GARAGE)), garage_trace)
		var ramps := {}
		for id: String in plan.modeled_vehicle_ramps:
			var stations: Array = plan.modeled_vehicle_ramps[id]
			var cross: Dictionary = stations.reduce(func(a: Dictionary,b: Dictionary) -> Dictionary:
				return a if absf(a.east_north[0]+103.) < absf(b.east_north[0]+103.) else b)
			var layers := column(cross.east_north)
			ramps[id] = layers
		check("separate_ramps_below_rail",
			layer_names(ramps["1256840000"]).has(RAMP_WEST) and layer_names(ramps["1324001438"]).has(RAMP_EAST)
			and layer_names(ramps["1256840000"]).has(RAIL) and layer_names(ramps["1324001438"]).has(RAIL), ramps)
		var inland: Array = plan.motor_ramp_footings["1256839997"][-1]
		var width := .9
		var origin := Vector3(inland[0],inland[3]-.55,-inland[1])
		var pier_hit := scene.get_world_3d().direct_space_state.intersect_ray(
			PhysicsRayQueryParameters3D.create(origin+Vector3.LEFT*width,origin+Vector3.RIGHT*width,1))
		var pier_name := String(pier_hit.collider.get_parent().name) if not pier_hit.is_empty() else ""
		var inland_contacts := column([inland[0],inland[1]])
		var head := inland_contacts.filter(func(hit: Array) -> bool: return hit[0] == pier_name)
		var head_height := -INF if head.is_empty() else float(head[0][1])-float(plan.camera_58_street_floor_game_m)
		check("photo_registered_round_pier", pier_name == "COL_Raijiapo_RampRoundColumns"
			and absf(head_height-13.)<.20 and not layer_names(inland_contacts).has("COL_Outer500_Court_56"),
			{"mesh":pier_name,"footing_enu_and_head":inland,
			"head_m_above_street":head_height,"column":inland_contacts})
		var outer: Array = plan.modeled_vehicle_ramps["1324001438"]
		for i in range(1,outer.size()-1):
			var p: Vector2 = Vector2(outer[i].east_north[0],outer[i].east_north[1])
			if absf(p.x+102.) > 1.7:
				continue
			var a: Array = outer[i-1].east_north
			var b: Array = outer[i+1].east_north
			var along := (Vector2(b[0],b[1])-Vector2(a[0],a[1])).normalized()
			var side := p+Vector2(along.y,-along.x)*2.38
			var edge := column([side.x,side.y])
			var rises := []
			for hit: Array in edge:
				if hit[0] == RAMP_EAST:
					rises.append(hit[1]-float(plan.camera_58_street_floor_game_m))
			check("street_facing_ramp_parapet_height", rises.size()==1 and rises[0]>17. and rises[0]<18.,
				{"enu": [side.x,side.y],"edge_above_street_m": rises,"column":edge})
			break
	return {"id":"changbin_street_to_bridge_park_58_to_61","stations":plan.route_east_north,
		"street_focus":[-154.55,-169.54,-4.78],"destination_y":plan.route_finish_m,
		"return_focus":[-62.0,-201.6,2.1]}

func roof_at(e: float) -> Array:
	var stations: Array = plan.parking.roof_game_east_north_up
	for i in range(stations.size()-1):
		var a: Array = stations[i]
		var b: Array = stations[i+1]
		if e >= a[0] and e <= b[0]:
			var weight := inverse_lerp(float(a[0]),float(b[0]),e)
			return [e,lerpf(a[1],b[1],weight),lerpf(a[2],b[2],weight)]
	return []

func layer_names(layers: Array) -> Array:
	return layers.map(func(hit: Array) -> String: return hit[0])

func ground_contact(point: Array) -> Array:
	for hit: Array in column(point):
		if hit[0].begins_with("COL_Outer500_Surface_") or hit[0] == "COL_Park57_EastWalkGrade":
			return hit
	return []

func road_clearance(pos: Array) -> float:
	var en := Vector2(pos[0],pos[1])
	var edge := INF
	for i in range(plan.road_axis.size()-1):
		var a := Vector2(plan.road_axis[i][0],plan.road_axis[i][1])
		var b := Vector2(plan.road_axis[i+1][0],plan.road_axis[i+1][1])
		var nearest := Geometry2D.get_closest_point_to_segment(en,a,b)
		if en.distance_to(nearest) < absf(edge):
			edge = en.distance_to(nearest) * signf((en-a).cross(b-a))
	return edge

func leg_without_placement(label: String, goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	var trace: Array = walks[-1].trace_enu
	var sites := {}
	for id: String in plan.plots:
		var station := Vector2(plan.plots[id][0],plan.plots[id][1])
		var nearest := [INF]
		for pos: Array in trace:
			var offset := Vector2(pos[0],pos[1]).distance_to(station)
			if offset < nearest[0]:
				nearest = [offset,pos]
		sites[id] = nearest
	var minimum := INF
	for pos: Array in trace:
		minimum = minf(minimum,road_clearance(pos))
	check(label+"_on_park_side",minimum>5.54,{"min_to_road_axis_m":minimum})
	check(label+"_visits_58_to_61",sites.values().all(func(row: Array) -> bool: return row[0]<.86),sites)
	return result

func eye_frame(label: String, focus: Variant) -> void:
	await super.eye_frame(label,focus)
	if label != "street":
		return
	for id: String in plan.street_views:
		var view: Dictionary = plan.street_views[id]
		await native_view("street-plot-"+id,view.eye_enu,view.target_enu,view.fov_deg,view.registered_heading_deg)
	if not baseline:
		var point: Array = plan.plots["58"]
		var floor := ground_contact(point)
		await native_view("bridge-and-parking-from-park",[point[0],point[1],floor[1]+1.68],[-103.,-156.,16.],75.)

func native_view(label: String, eye: Array, target: Array, fov: float, heading: Variant = null) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.position=Vector3(eye[0],eye[2],-eye[1])
	camera.look_at(Vector3(target[0],target[2],-target[1]))
	camera.fov=fov
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var name := label+".png"
	var saved := root.get_texture().get_image().save_png(output.path_join(name))
	check("registered_native_"+label,saved==OK,name)
	view_positions.append({"frame":name,"eye_enu":eye,"target_enu":target,
		"registered_heading_deg":heading,"fov_deg":fov,"pixel_size":str(root.size)})
	scene.explorer.camera.make_current()
	camera.queue_free()
