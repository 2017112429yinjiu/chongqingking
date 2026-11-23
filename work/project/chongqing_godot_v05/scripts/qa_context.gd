extends RefCounted
## Preserve older acceptance records while binding new reports to active art.
static func directory(fallback: String="res://verification_r18") -> String:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--qa-dir="):
			return arg.trim_prefix("--qa-dir=")
	return fallback

static func decorate(report: Dictionary, main: Node3D) -> void:
	report["art_profile"]={"path":main.art_profile_path,"sha256":FileAccess.get_sha256(main.art_profile_path),"revision":main.art_profile.get("art_revision","")}
	report["street_layer"]=main.scene_identity.get("street_r19",{})
	report["upper_lane"]=main.scene_identity.get("upper_lane",{})
	report["meter_lod"]=main.scene_identity.get("meter_lod",{})
	if main.scene_identity.has("street_use_r24"):
		report["street_use_r24"]=main.scene_identity["street_use_r24"]
	if main.scene_identity.has("counter_r21"):
		report["counter_r21"]=main.scene_identity.counter_r21
	if main.scene_identity.has("district_r21"):
		report["district_r21"]=main.scene_identity.district_r21
	if main.scene_identity.has("roofs_r22"):
		report["roofs_r22"]=main.scene_identity.roofs_r22
	if main.scene_identity.has("river_r22"):
		report["river_r22"]=main.scene_identity.river_r22
	if main.scene_identity.has("court_resident"):
		report["court_resident"]=main.scene_identity.court_resident
	report["runtime_sha256"]={}
	if main.scene_identity.has("district_connections"):
		report["district_connections"]=main.scene_identity.district_connections
		for path in ["res://scripts/district_connections_r24.gd","res://assets/connections_r24/connections.glb","res://assets/connections_r24/layout.json","res://shaders/joined_stone_r24.gdshader","res://shaders/noodle_surfaces_r24.gdshader","res://shaders/noodle_steam_r24.gdshader","res://assets/connections_r24/soup_notice.jpg"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("east_lane_joint"):
		report["east_lane_joint"]=main.scene_identity.east_lane_joint
		var donor: String = "res://assets/lane_inlets_r24/junction.glb" if main.art_profile.get("east_alley_inlets_r24",false) else "res://assets/lane_connection_r24/junction.glb"
		if main.art_profile.get("east_alley_inlets_r24",false):
			report.runtime_sha256["res://assets/lane_inlets_r24/inlets.json"]=FileAccess.get_sha256("res://assets/lane_inlets_r24/inlets.json")
		for path in ["res://scripts/lane_connection_r24.gd",donor,"res://assets/lane_connection_r24/layout.json","res://shaders/lane_steps_r24.gdshader","res://shaders/lane_pavers_r24.gdshader"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.get("market_passing_r24",false):
		for path in ["res://scripts/pedestrian_passing_r24.gd","res://assets/market_steps_r24/passing_space.json","res://scripts/explorer.gd","res://scripts/scooter_controller.gd"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("market_steps"):
		report["market_steps"] = main.scene_identity.market_steps
		for path in ["res://assets/market_steps_r24/market.glb","res://scripts/market_steps_r24.gd","res://shaders/market_sandstone_r24.gdshader"]:
			report.runtime_sha256[path] = FileAccess.get_sha256(path)
	if main.art_profile.get("wall_occlusion_r24", false):
		var wall_resource := "res://assets/vertical_run/interior_wall_faces.res"
		for part:String in ["scripts/unit_interior.gd","scripts/blue_stair.gd","scripts/passage_order.gd","assets/vertical_run/layout.json","assets/vertical_run/vertical.glb"]:
			report.runtime_sha256["res://"+part]=FileAccess.get_sha256("res://"+part)
		report.runtime_sha256[wall_resource] = FileAccess.get_sha256(wall_resource)
	if main.scene_identity.has("window_rooms"):
		report["window_rooms"]=main.scene_identity.window_rooms
		for path in ["res://scripts/window_life_r24.gd","res://assets/rooms_r24/rooms.glb","res://assets/rooms_r24/layout.json"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
		if main.art_profile.get("room_patina_r24",false):
			for path in ["res://shaders/wall_patina_r24.gdshader","res://assets/rooms_r24/patina.json","res://assets/rooms_r24/patina.glb"]:
				report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.get("fitted_kitchen_r24",false):
		for path in ["res://assets/courtyard_r24/kitchen/courtyard.glb","res://assets/courtyard_r24/kitchen/layout.json","res://assets/courtyard_r24/kitchen/greens_motion.glb"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("courtyard_paving"):
		report["courtyard_paving"]=main.scene_identity.courtyard_paving
		report.runtime_sha256["res://assets/courtyard_r24/paving.glb"]=FileAccess.get_sha256("res://assets/courtyard_r24/paving.glb")
	if main.scene_identity.has("neighborhood"):
		report["neighborhood"]=main.scene_identity.neighborhood
		for path in ["res://scripts/neighborhood_r24.gd","res://assets/neighborhood_r24/street.glb","res://assets/neighborhood_r24/layout.json","res://assets/neighborhood_r24/walk_lanes.json","res://assets/neighborhood_r24/trunk_sections.json","res://shaders/pedestrian_outerwear_r24.gdshader"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.has("washcloth_shader"):
		var cloth_path: String = main.art_profile["washcloth_shader"]
		report.runtime_sha256[cloth_path] = FileAccess.get_sha256(cloth_path)
		var pile_path := "res://assets/frontage_r24/terry_pile.png"
		report.runtime_sha256[pile_path] = FileAccess.get_sha256(pile_path)
	if main.scene_identity.has("street_use_r24"):
		for path in ["res://scripts/street_use_r24.gd","res://assets/street_use_r24/workday.glb","res://assets/street_use_r24/layout.json","res://assets/street_use_r24/street_use.png","res://assets/street_use_r24/support_heights.png","res://shaders/dressed_stone_r24.gdshader","res://shaders/asphalt_use_r24.gdshader","res://shaders/street_use_r24.gdshaderinc","res://shaders/street_repairs_r24.gdshaderinc","res://shaders/foundation_r23.gdshader","res://shaders/sidewalk_r23.gdshader","res://shaders/frontage_surface_r24.gdshader"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("courtyard_life"):
		report["courtyard_life"]=main.scene_identity.courtyard_life
		for path in ["res://scripts/courtyard_life_r24.gd","res://assets/courtyard_r24/courtyard.glb","res://assets/courtyard_r24/layout.json","res://assets/courtyard_r24/west_plaster.png","res://shaders/street_surface_r19.gdshader","res://assets/courtyard_r24/red_motion.glb","res://assets/courtyard_r24/black_motion.glb","res://assets/courtyard_r24/greens_motion.glb"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.get("natural_stops_r24",false):
		for path in ["res://assets/courtyard_r24/return_corridors.json","res://assets/courtyard_r24/wait_clips.res","res://assets/frontage_r24/stall_clips.res"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.get("canopy_distance_r24",false):
		for path in ["res://assets/neighborhood_r24/tree_distances.glb","res://assets/neighborhood_r24/tree_species.json"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.art_profile.get("traffic_lanes_r24",false):
		var lane_path:="res://assets/frontage_r24/traffic_lanes.json"
		report.runtime_sha256[lane_path]=FileAccess.get_sha256(lane_path)
		var shade_path:="res://assets/frontage_r24/tyre_contact.png"
		report.runtime_sha256[shade_path]=FileAccess.get_sha256(shade_path)
	if main.scene_identity.has("market_r24"):
		report["market_r24"]=main.scene_identity.market_r24
		for path in ["res://assets/frontage_r24/frontage.glb","res://assets/frontage_r24/frontage.json","res://assets/frontage_r24/stall_clips.res","res://scripts/frontage_r24.gd","res://shaders/frontage_surface_r24.gdshader","res://shaders/frontage_canvas_r24.gdshader","res://shaders/stall_enamel_r24.gdshader"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("block_r23"):
		report["block_r23"]=main.scene_identity.block_r23
		for path in ["res://assets/block_r23/block.glb","res://assets/block_r23/routes.json","res://assets/block_r23/block.json","res://scripts/block_r23.gd","res://scripts/scooter_controller.gd","res://scripts/explorer.gd"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("river_r22"):
		for path in ["res://scripts/river_r22.gd","res://scripts/roofs_r22.gd","res://shaders/river_r22.gdshader","res://shaders/riverbank_r22.gdshader","res://shaders/river_foliage_r22.gdshader","res://shaders/breakfast_canvas_r22.gdshader","res://assets/river_r22/shore_masks.png"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	for path in ["res://scripts/shopkeeper.gd","res://scripts/shopkeeper_attention.gd","res://scripts/takeaway_bag.gd","res://scripts/counter_condiments.gd"]:
		report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if main.scene_identity.has("district_r21"):
		for path in ["res://scripts/district_r21.gd","res://shaders/paving_r21.gdshader","res://shaders/exterior_r21.gdshader","res://shaders/canopy_r21.gdshader","res://shaders/worn_rail_r21.gdshader"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
	for path in ["res://scripts/main.gd","res://scripts/street_detail_r19.gd","res://shaders/street_surface_r19.gdshader","res://shaders/sky_visibility_r20.gdshaderinc","res://scripts/upper_lane_r20.gd"]:
		report.runtime_sha256[path]=FileAccess.get_sha256(path)
	if not report.upper_lane.is_empty():
		for path in ["res://assets/lane_r20/tree_seats.json","res://scripts/explorer.gd"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
		report.runtime_sha256["res://shaders/rinse_water.gdshader"]=FileAccess.get_sha256("res://shaders/rinse_water.gdshader")
		report.runtime_sha256["res://scripts/meter_detail_lod.gd"]=FileAccess.get_sha256("res://scripts/meter_detail_lod.gd")
		for path in ["res://scripts/gameplay.gd", "res://scripts/qa_lane_r20.gd", "res://scripts/rinse_tap.gd", "res://assets/lane_r20/rinse.wav", "res://assets/lane_r20/rinse_fixture.json", "res://shaders/hanging_cotton_r20.gdshader", "res://assets/fonts/cq_lane_ui.otf"]:
			report.runtime_sha256[path]=FileAccess.get_sha256(path)
