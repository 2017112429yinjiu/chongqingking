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
