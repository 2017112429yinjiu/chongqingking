extends Node3D
## Real imported mesh inspection, with a small pickup/dropoff interaction.
## Viewpoints and verification routes are authored in assets/viewpoints.json.

const ExplorerScript = preload("res://scripts/explorer.gd")
const GameplayScript = preload("res://scripts/gameplay.gd")
@export var first_day_enabled := false
@export var district_500_enabled := false
var gameplay: Node3D
const CollisionBuilder = preload("res://scripts/build_collisions.gd")
const UI_FONT = preload("res://assets/fonts/cq_district_ui.otf")
const DEFAULT_ART_PROFILE = "res://assets/render_profile_r24.json"
var street_block: Node3D
var VIEW_NAMES: Array[String] = []
var view_picker: OptionButton
var capture_mode: bool = false
var startup_ms: int = 0
var sky_profile: Dictionary = {"procedural_clouds": false}
var art_profile: Dictionary = {}
var art_profile_path: String = DEFAULT_ART_PROFILE
var applied_lighting: Dictionary = {}
var reflection_profile: Dictionary = {}
var glass_materials: Dictionary = {}
var safe_leaf_materials: Dictionary = {}
var branch_materials: Dictionary = {}
var practical_profile: Dictionary = {"street_lights": 0, "interior_lights": [], "interior_candidate_count": 0}
var gi_profile: Dictionary = {"requested": false, "enabled": false, "structures_only": false}
var scene_identity: Dictionary = {}
var material_stats: Dictionary = {"surfaces": 0, "vertex_color_surfaces": 0, "static_gi_meshes": 0, "gi_excluded_meshes": 0, "specular_adjusted_materials": {}, "tile_diagnostics": {}}

var explorer: Node3D
var collision_stats: Dictionary = {}
var survey_sample_adjustments: Array = []
var config: Dictionary = {}
var hud: Control
var mode_button: Button
var mode_label: Label
var controls_label: Label
var objective_label: Label
var prompt_label: Label
var _elapsed: float = 0.0
var _delivery_stage: int = 0
var _pickup: Vector3
var _dropoff: Vector3
var _toast_remaining: float = 0.0


func _ready() -> void:
	startup_ms = Time.get_ticks_msec()
	capture_mode = "--capture" in OS.get_cmdline_user_args() or "--r18-motion" in OS.get_cmdline_user_args() or "--r18-rider-motion" in OS.get_cmdline_user_args()
	if _gi_qa_requested() and (DisplayServer.get_name() == "headless" or RenderingServer.get_current_rendering_method() != "forward_plus" or RenderingServer.get_rendering_device() == null):
		push_error("The SDFGI image experiment requires an active Forward+ rendering device and display.")
		get_tree().quit(3)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/viewpoints.json"))
	if not parsed is Dictionary:
		push_error("Missing or invalid assets/viewpoints.json")
		get_tree().quit(2)
		return
	config = parsed
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--art-profile="):
			art_profile_path = arg.trim_prefix("--art-profile=")
	if FileAccess.file_exists(art_profile_path):
		var art_parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(art_profile_path))
		if art_parsed is Dictionary:
			art_profile = art_parsed
	var active_revision := str(art_profile.get("art_revision", "")).get_slice("_", 0)
	get_window().title = str(art_profile.get("window_title", ("重庆外卖王 · 梯坎里 " + active_revision).strip_edges()))
	if capture_mode or "--smoke-test" in OS.get_cmdline_user_args() or "--survey-test" in OS.get_cmdline_user_args():
		_read_scene_identity()
	if "--survey-test" in OS.get_cmdline_user_args():
		_apply_survey_sample_adjustments()
	# External diagnostic cameras are runtime-only; the authored 14-view UI stays unchanged.
	var diagnostic_views: Dictionary = art_profile.get("diagnostic_views", {})
	if not diagnostic_views.is_empty():
		config["views"].merge(diagnostic_views, true)
		for diagnostic_name in diagnostic_views:
			if not config["view_order"].has(diagnostic_name):
				config["view_order"].append(diagnostic_name)
	var available_views: Dictionary = config.get("views", {})
	var ordered: Array = config.get("view_order", available_views.keys())
	for key in ordered:
		if available_views.has(str(key)):
			VIEW_NAMES.append(str(key))
	if VIEW_NAMES.is_empty():
		push_error("No valid camera views configured")
		get_tree().quit(2)
		return
	if not has_node("City") or not has_node("WorldEnvironment") or $WorldEnvironment.environment == null:
		push_error("Missing City or WorldEnvironment; cannot run or capture this district.")
		get_tree().quit(2)
		return
	if $WorldEnvironment.environment.background_mode == Environment.BG_SKY and $WorldEnvironment.environment.sky == null:
		push_error("Sky background is enabled but no sky resource is assigned.")
		get_tree().quit(2)
		return
	_pickup = _vec3(config.get("pickup", [-32, 11.35, 72]))
	_dropoff = _vec3(config.get("dropoff", [-38, 14.95, 40]))
	_apply_renderer_profile()
	_build_practicals()
	scene_identity["street_r19"] = preload("res://scripts/street_detail_r19.gd").apply($City, art_profile)
	if art_profile.get("lane_r20", false):
		scene_identity["upper_lane"] = preload("res://scripts/upper_lane_r20.gd").install($City, capture_mode)
	if art_profile.get("meter_lod", false):
		scene_identity["meter_lod"]=preload("res://scripts/meter_detail_lod.gd").install($City)
	_configure_materials($City)
	scene_identity["street_r19_surfaces"] = preload("res://scripts/street_detail_r19.gd").surfaces($City, art_profile)
	if art_profile.get("district_r21",false):
		scene_identity["district_r21"]=preload("res://scripts/district_r21.gd").install($City, 250.0 if district_500_enabled else 0.0)
	if art_profile.get("roofs_r22",false):
		scene_identity["roofs_r22"]=preload("res://scripts/roofs_r22.gd").install($City)
		if art_profile.has("surface_import_revision"):
			scene_identity["roofs_r22"]["surface_imports_sha256"]=FileAccess.get_sha256("res://assets/roofs_r22/surface_imports.json")
	if art_profile.get("river_r22",false):
		scene_identity["river_r22"]=preload("res://scripts/river_r22.gd").new().install($City)
	if art_profile.get("block_r23",false):
		street_block = preload("res://scripts/block_r23.gd").new()
		street_block.name = "StreetBlockR23"
		$City.add_child(street_block)
		var lane_data: Dictionary={}
		if art_profile.get("traffic_lanes_r24",false):
			lane_data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/frontage_r24/traffic_lanes.json"))
		var cloth_shader: Shader = load(art_profile["washcloth_shader"]) if art_profile.has("washcloth_shader") else null
		scene_identity["block_r23"] = street_block.install($City,lane_data,cloth_shader)
	if art_profile.get("market_r24",false):
		var frontage:=preload("res://scripts/frontage_r24.gd").new()
		frontage.name="MarketTerraceR24"
		$City.add_child(frontage)
		scene_identity["market_r24"]=frontage.install($City)
	if art_profile.get("street_finish_r24",false):
		var finish:=preload("res://scripts/city_frame_r24.gd").new()
		finish.name="StreetFinishR24"
		$City.add_child(finish)
		scene_identity["street_finish_r24"]=finish.install($City, not district_500_enabled)
	if art_profile.get("street_use_r24",false):
		scene_identity["street_use_r24"]=preload("res://scripts/street_use_r24.gd").install($City)
	if art_profile.get("neighborhood_r24",false):
		scene_identity["neighborhood"]=preload("res://scripts/neighborhood_r24.gd").install($City,street_block,art_profile.get("canopy_distance_r24",false))
	if art_profile.get("courtyard_life_r24",false):
		var courtyard:=preload("res://scripts/courtyard_life_r24.gd").new()
		courtyard.name="CourtyardLife14"
		$City.add_child(courtyard)
		scene_identity["courtyard_life"]=courtyard.install($City,street_block,art_profile.get("fitted_kitchen_r24",false))
	if art_profile.get("courtyard_paving_r24",false):
		scene_identity["courtyard_paving"]=preload("res://scripts/courtyard_life_r24.gd").install_paving($City)
	if art_profile.get("window_life_r24",false):
		scene_identity["window_rooms"]=preload("res://scripts/window_life_r24.gd").install($City,art_profile.get("room_patina_r24",false))
	if art_profile.get("market_steps_r24", false):
		scene_identity["market_steps"] = preload("res://scripts/market_steps_r24.gd").install($City)
	if art_profile.get("east_lane_joint_r24",false):
		scene_identity["east_lane_joint"] = preload("res://scripts/lane_connection_r24.gd").install($City,false,art_profile.get("east_alley_inlets_r24",false))
	if art_profile.get("district_connections_r24",false):
		scene_identity["district_connections"]=preload("res://scripts/district_connections_r24.gd").install($City,false,{},street_block)
	if art_profile.get("wall_occlusion_r24", false):
		var walls := OccluderInstance3D.new()
		walls.name = "OpaqueFacadeOcclusion"
		walls.occluder = load("res://assets/district_patrol/interior_wall_faces.res")
		$City.add_child(walls)
		get_viewport().use_occlusion_culling = true
	_build_reflection_probes()
	if district_500_enabled:
		scene_identity["district_500"] = preload("res://scripts/district_500.gd").install($City)
	collision_stats = CollisionBuilder.attach($City)
	collision_stats["props"] = preload("res://scripts/prop_collisions.gd").attach($City)
	_build_hud()
	await get_tree().physics_frame
	await get_tree().physics_frame
	explorer = ExplorerScript.new()
	if art_profile.get("market_passing_r24", false):
		explorer.walk_collision_mask |= preload("res://scripts/pedestrian_passing_r24.gd").PEOPLE_LAYER
	explorer.name = "Explorer"
	add_child(explorer)
	var points: Dictionary = {}
	var views: Dictionary = config.get("views", {})
	for view_name in VIEW_NAMES:
		var view: Dictionary = views.get(view_name, {})
		if not view.is_empty():
			points[view_name] = {"position": _vec3(view.position), "target": _vec3(view.target), "fov": float(view.get("fov", 64))}
	points["walk_spawn"] = _vec3(config.get("walk_spawn", [-27, 11.45, 78]))
	points["walk_target"] = _vec3(config.get("walk_target", [-30, 14, 57]))
	explorer.setup(points)
	if scene_identity.get("street_finish_r24",{}).get("local_frame",false):
		explorer.camera.far=3600.0
	gameplay = GameplayScript.new()
	gameplay.name = "InteractionWorld"
	add_child(gameplay)
	gameplay.setup(self)
	if district_500_enabled:
		gameplay.shancheng=preload("res://scripts/shancheng_delivery.gd").new()
		gameplay.add_child(gameplay.shancheng)
		gameplay.shancheng.setup(gameplay)
		var outer_district := $City.get_node("OuterDistrict500")
		if outer_district.has_meta("riverside_tea"):
			var tea: Dictionary=outer_district.get_meta("riverside_tea")
			gameplay.riverside_tea=preload("res://scripts/shancheng_delivery.gd").new()
			gameplay.riverside_tea.name="RiversideTeaHandoff"
			gameplay.add_child(gameplay.riverside_tea)
			gameplay.riverside_tea.setup(gameplay,tea.public_stops)
		explorer.recovery_half_extent_m = 251.0
		gameplay.scooter.recovery_half_extent_m = 251.0
		gameplay.scooter.recovery_min_height_m = -19.0
	if art_profile.get("market_passing_r24", false):
		gameplay.scooter.collision_mask |= preload("res://scripts/pedestrian_passing_r24.gd").PEOPLE_LAYER
	if street_block:
		explorer.install_walking_body(load("res://assets/block_r23/body_view.glb"))
		gameplay.bind_walking_hand()
		street_block.start_simulation(self)
	var market=$City.get_node_or_null("MarketTerraceR24")
	if market:market.start_life(self)
	var courtyard=$City.get_node_or_null("CourtyardLife14")
	if courtyard:courtyard.start(self)
	explorer.mode_changed.connect(_mode_changed)
	explorer.view_changed.connect(_view_changed)
	if district_500_enabled and "--explore-500" in OS.get_cmdline_user_args():
		preload("res://scripts/district_500.gd").start_exploration(self)
	elif first_day_enabled and not capture_mode and not Array(OS.get_cmdline_user_args()).any(func(arg: String): return arg == "--r16-performance" or (arg.ends_with("-test") and arg != "--day-one-test")):
		gameplay.lesson = preload("res://scripts/day_one.gd").new()
		gameplay.lesson.name = "FirstShift"
		gameplay.add_child(gameplay.lesson)
		gameplay.lesson.setup(gameplay)
	elif "--smoke-test" in OS.get_cmdline_user_args() or "--survey-test" in OS.get_cmdline_user_args():
		explorer.set_mode(true)
	else:
		# Start at the pedestrian-scale material review view without reordering shortcuts.
		explorer.go_to_view("r23_main_road" if street_block else "central_steps")
	_mode_changed(explorer.walking)
	print("CQ_READY ", JSON.stringify({"engine": Engine.get_version_info().string, "renderer": RenderingServer.get_current_rendering_method(), "collisions": collision_stats, "spawn": config.get("walk_spawn")}))
	if "--r23-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_block_r23.gd").run(self)
	elif "--r20-lane-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_lane_r20.gd").run(self)
	elif "--r19-street-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_street_r19.gd").run(self)
	elif "--r18-rider-motion" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_rider_motion.gd").run(self)
	elif "--r18-rider-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_rider.gd").run(self)
	elif "--r18-motion" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_shopkeeper_motion.gd").run(self)
	elif "--r18-shopkeeper-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_shopkeeper_performance.gd").run(self)
	elif "--r17-character-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_character.gd").run(self)
	elif "--r17-delivery-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_delivery.gd").run(self)
	elif "--r16-test" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_gameplay.gd").run(self)
	elif "--r16-performance" in OS.get_cmdline_user_args():
		await preload("res://scripts/qa_performance.gd").run(self)
	elif "--smoke-test" in OS.get_cmdline_user_args() or "--survey-test" in OS.get_cmdline_user_args():
		_run_smoke_test("--survey-test" in OS.get_cmdline_user_args())
	elif "--capture" in OS.get_cmdline_user_args():
		_capture_views()


func _vec3(value: Variant) -> Vector3:
	if value is Array and value.size() == 3:
		return Vector3(float(value[0]), float(value[1]), float(value[2]))
	return Vector3.ZERO


func _array(v: Vector3) -> Array:
	return [snappedf(v.x, 0.001), snappedf(v.y, 0.001), snappedf(v.z, 0.001)]


func _read_scene_identity() -> void:
	var path: String = "res://assets/chongqing_district.glb"
	scene_identity = {"asset": path, "sha256": FileAccess.get_sha256(path), "bytes": 0, "revision": null}
	var asset: FileAccess = FileAccess.open(path, FileAccess.READ)
	if asset:
		scene_identity["bytes"] = asset.get_length()
		asset.close()
	if FileAccess.file_exists("res://assets/scene_manifest.json"):
		var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/scene_manifest.json"))
		if manifest is Dictionary:
			scene_identity["revision"] = manifest.get("revision", null)


func _gi_qa_requested() -> bool:
	return "--qa-sdfgi" in OS.get_cmdline_user_args() or "--qa-sdfgi-structures" in OS.get_cmdline_user_args()


func _apply_survey_sample_adjustments() -> void:
	if not FileAccess.file_exists("res://assets/walking_survey.json"):
		return
	var supplemental: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/walking_survey.json"))
	if not supplemental is Dictionary:
		return
	for adjustment in supplemental.get("sample_adjustments", []):
		var match_xz: Array = adjustment.get("match_xz", [])
		if match_xz.size() != 2:
			continue
		for key in ["ground_samples", "clearance_samples"]:
			var samples: Array = config.get(key, [])
			for index in range(samples.size()):
				var sample: Vector3 = _vec3(samples[index])
				if Vector2(sample.x - float(match_xz[0]), sample.z - float(match_xz[1])).length() < 0.01:
					survey_sample_adjustments.append({"list": key, "index": index, "original": samples[index], "replacement": adjustment.replacement, "reason": adjustment.get("reason", "Authored walking-surface sample correction")})
					samples[index] = adjustment.replacement


func _lighting_config() -> Dictionary:
	var method: String = RenderingServer.get_current_rendering_method()
	var profile: Dictionary = config.get("lighting", {}).duplicate(true)
	profile.merge(config.get("lighting_profiles", {}).get(method, {}), true)
	profile.merge(art_profile.get("lighting", {}), true)
	profile.merge(art_profile.get("lighting_profiles", {}).get(method, {}), true)
	return profile


func _apply_renderer_profile() -> void:
	var environment: Environment = $WorldEnvironment.environment
	var profile: Dictionary = _lighting_config()
	applied_lighting = profile.duplicate(true)
	var forward: bool = RenderingServer.get_current_rendering_method() == "forward_plus"
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES if forward else Environment.TONE_MAPPER_LINEAR
	environment.tonemap_exposure = float(profile.get("exposure", 1.05 if forward else 1.0))
	# Keep highlight headroom in the tonemapper, rather than applying a
	# post-process brightness/contrast lift to the shaded surfaces.
	environment.tonemap_white = float(profile.get("tonemap_white", 1.0))
	environment.ambient_light_energy = float(profile.get("ambient_energy", 0.58 if forward else 0.42))
	environment.fog_enabled = bool(profile.get("fog", true))
	environment.fog_density = float(profile.get("fog_density", 0.0013))
	environment.fog_light_energy = float(profile.get("fog_light_energy", 0.8))
	environment.fog_aerial_perspective = float(profile.get("fog_aerial_perspective", 0.3))
	environment.fog_sky_affect = float(profile.get("fog_sky_affect", 0.15))
	environment.background_energy_multiplier = float(profile.get("background_energy", 1.0))
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	environment.ambient_light_sky_contribution = float(profile.get("sky_contribution", 1.0))
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	environment.ssil_enabled = forward and bool(profile.get("ssil", false))
	environment.ssil_radius = float(profile.get("ssil_radius", 2.4))
	environment.ssil_intensity = float(profile.get("ssil_intensity", 0.28))
	environment.ssil_sharpness = float(profile.get("ssil_sharpness", 0.96))
	environment.ssil_normal_rejection = float(profile.get("ssil_normal_rejection", 1.0))
	environment.ssao_enabled = forward and bool(profile.get("ssao", true))
	environment.ssao_radius = float(profile.get("ssao_radius", 1.7))
	environment.ssao_intensity = float(profile.get("ssao_intensity", 1.25))
	environment.ssao_power = float(profile.get("ssao_power", 1.3))
	environment.ssao_detail = float(profile.get("ssao_detail", 0.65))
	environment.ssao_light_affect = float(profile.get("ssao_light_affect", 0.16))
	if forward and profile.has("ssao_half_size"):
		RenderingServer.environment_set_ssao_quality(RenderingServer.ENV_SSAO_QUALITY_MEDIUM, bool(profile.ssao_half_size), 0.5, 2, 50.0, 300.0)
	environment.ssr_enabled = forward and bool(profile.get("ssr", false))
	environment.glow_enabled = forward and bool(profile.get("glow", true))
	environment.glow_intensity = float(profile.get("glow_intensity", 0.22))
	environment.glow_bloom = float(profile.get("glow_bloom", 0.05))
	environment.adjustment_enabled = bool(profile.get("adjustment", true))
	environment.adjustment_brightness = float(profile.get("brightness", 1.0))
	environment.adjustment_contrast = float(profile.get("contrast", 1.025))
	environment.adjustment_saturation = float(profile.get("saturation", 0.95))
	$Sun.light_angular_distance = float(profile.get("sun_angular_distance", 1.5))
	$Sun.directional_shadow_max_distance = float(profile.get("shadow_max_distance", profile.get("shadow_distance", 180.0)))
	$Sun.shadow_bias = float(profile.get("shadow_bias", 0.08))
	$Sun.shadow_normal_bias = float(profile.get("shadow_normal_bias", 1.0))
	$Sun.directional_shadow_split_1=float(profile.get("shadow_split_1",.1))
	$Sun.directional_shadow_split_2=float(profile.get("shadow_split_2",.2))
	$Sun.directional_shadow_split_3=float(profile.get("shadow_split_3",.5))
	$Sun.light_specular = float(profile.get("sun_specular", 1.0 if forward else 0.6))
	$Sun.shadow_enabled = bool(profile.get("sun_shadows", true)) and not "--qa-no-sun-shadows" in OS.get_cmdline_user_args()
	$Sun.light_energy = float(profile.get("sun_energy", 1.35 if forward else 0.50))
	if profile.has("sun_rotation_deg"):
		$Sun.rotation_degrees = _vec3(profile.sun_rotation_deg)
	if profile.has("sun_color"):
		var rgb: Vector3 = _vec3(profile.sun_color)
		$Sun.light_color = Color(rgb.x, rgb.y, rgb.z)
	if profile.has("ambient_color"):
		var rgb: Vector3 = _vec3(profile.ambient_color)
		environment.ambient_light_color = Color(rgb.x, rgb.y, rgb.z)
	if profile.has("fog_color"):
		var rgb: Vector3 = _vec3(profile.fog_color)
		environment.fog_light_color = Color(rgb.x, rgb.y, rgb.z)
	_configure_overcast_sky(environment, profile)
	_configure_global_illumination(environment, profile)


func _configure_global_illumination(environment: Environment, profile: Dictionary) -> void:
	var requested: bool = _gi_qa_requested() or bool(profile.get("sdfgi_enabled", false))
	var structures: bool = "--qa-sdfgi-structures" in OS.get_cmdline_user_args() or bool(profile.get("sdfgi_structures", false))
	var supported: bool = DisplayServer.get_name() != "headless" and RenderingServer.get_current_rendering_method() == "forward_plus" and RenderingServer.get_rendering_device() != null
	gi_profile = {"requested": requested, "enabled": requested and supported, "structures_only": structures, "explicit_experiment": _gi_qa_requested()}
	environment.sdfgi_enabled = requested and supported
	if not environment.sdfgi_enabled:
		if requested:
			gi_profile["reason"] = "Production GI is skipped for headless physics checks or a renderer without Forward+ support"
		return
	environment.sdfgi_cascades = 4
	environment.sdfgi_min_cell_size = float(profile.get("sdfgi_cell_metres", 1.0))
	environment.sdfgi_read_sky_light = true
	environment.sdfgi_energy = float(profile.get("sdfgi_energy", 0.85))
	environment.sdfgi_bounce_feedback = 0.3
	environment.sdfgi_use_occlusion = false
	if structures:
		# SDFGI uses the real radiance sky as its environment input in this
		# profile, instead of inheriting the original flat-color ambient source.
		environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
		environment.ambient_light_sky_contribution = 1.0
		environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	RenderingServer.gi_set_use_half_resolution(true)
	RenderingServer.environment_set_sdfgi_ray_count(RenderingServer.ENV_SDFGI_RAY_COUNT_16)
	RenderingServer.environment_set_sdfgi_frames_to_converge(RenderingServer.ENV_SDFGI_CONVERGE_IN_5_FRAMES)
	RenderingServer.environment_set_sdfgi_frames_to_update_light(RenderingServer.ENV_SDFGI_UPDATE_LIGHT_IN_4_FRAMES)
	gi_profile.merge({"cascades": environment.sdfgi_cascades, "cell_metres": environment.sdfgi_min_cell_size, "read_sky": environment.sdfgi_read_sky_light, "energy": environment.sdfgi_energy, "rays_per_probe": 16, "half_resolution": true, "ambient_source": environment.ambient_light_source, "sky_contribution": environment.ambient_light_sky_contribution}, true)
	print("CQ_SDFGI_PROBE ", JSON.stringify(gi_profile))


func _configure_overcast_sky(environment: Environment, profile: Dictionary) -> void:
	var panorama_path: String = str(profile.get("hdri_path", ""))
	if not panorama_path.is_empty() and ResourceLoader.exists(panorama_path):
		var panorama: Texture2D = load(panorama_path) as Texture2D
		if panorama != null:
			var panorama_material: PanoramaSkyMaterial = PanoramaSkyMaterial.new()
			panorama_material.panorama = panorama
			panorama_material.energy_multiplier = float(profile.get("hdri_energy", 1.0))
			var panorama_sky: Sky = Sky.new()
			panorama_sky.sky_material = panorama_material
			panorama_sky.process_mode = Sky.PROCESS_MODE_QUALITY
			panorama_sky.radiance_size = Sky.RADIANCE_SIZE_256
			environment.sky = panorama_sky
			environment.background_mode = Environment.BG_SKY
			var rotation_degrees: Vector3 = _vec3(profile.get("hdri_rotation_deg", [0,0,0]))
			environment.sky_rotation = rotation_degrees * PI / 180.0
			sky_profile = {"type":"photographic_hdr_panorama", "path":panorama_path, "sha256":FileAccess.get_sha256(panorama_path), "energy":panorama_material.energy_multiplier, "rotation_degrees":_array(rotation_degrees), "radiance_size":256, "procedural_clouds":false}
			return
	var enabled: bool = bool(profile.get("procedural_clouds", config.get("procedural_clouds", false)))
	sky_profile = {"procedural_clouds": enabled}
	if not enabled:
		return
	var shader: Shader = load("res://shaders/chongqing_overcast.gdshader") as Shader
	if shader == null:
		push_error("The optional overcast shader could not be loaded")
		sky_profile["procedural_clouds"] = false
		return
	var material: ShaderMaterial = ShaderMaterial.new()
	material.shader = shader
	for key in ["cloud_coverage", "cloud_strength", "cloud_scale", "cloud_seed"]:
		var defaults: Dictionary = {"cloud_coverage": 0.76, "cloud_strength": 0.62, "cloud_scale": 1.35, "cloud_seed": 17.0}
		var value: float = float(profile.get(key, config.get(key, defaults[key])))
		if key in ["cloud_coverage", "cloud_strength"]:
			value = clampf(value, 0.0, 1.0)
		material.set_shader_parameter(key, value)
		sky_profile[key] = value
	for key in ["zenith_color", "horizon_color", "cloud_light_color", "cloud_shadow_color", "lower_hemisphere_color"]:
		if profile.has(key):
			var color: Vector3 = _vec3(profile[key])
			material.set_shader_parameter(key, Color(color.x, color.y, color.z))
	var sky: Sky = Sky.new()
	sky.sky_material = material
	sky.process_mode = Sky.PROCESS_MODE_QUALITY
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	environment.sky = sky
	environment.background_mode = Environment.BG_SKY


func _build_practicals() -> void:
	var profile: Dictionary = _lighting_config()
	var default_fills: Array = []
	if RenderingServer.get_current_rendering_method() == "gl_compatibility":
		default_fills = [
			{"rotation_deg": [-55, 145, 0], "color": [0.64, 0.76, 0.87], "energy": 0.08},
			{"rotation_deg": [-24, 70, 0], "color": [0.91, 0.87, 0.78], "energy": 0.04}
		]
	for spec in profile.get("ambient_fills", default_fills):
		var fill: DirectionalLight3D = DirectionalLight3D.new()
		fill.name = "SkyBounceFill"
		fill.rotation_degrees = _vec3(spec.get("rotation_deg", [-45, 140, 0]))
		var color: Vector3 = _vec3(spec.get("color", [0.7, 0.8, 0.9]))
		fill.light_color = Color(color.x, color.y, color.z)
		fill.light_energy = float(spec.get("energy", 0.08))
		fill.light_specular = 0.25
		fill.shadow_enabled = false
		$PracticalLights.add_child(fill)
	for spec in config.get("lights", []):
		if not spec is Dictionary:
			continue
		var light: OmniLight3D = OmniLight3D.new()
		light.name = str(spec.get("name", "StreetLight"))
		light.position = _vec3(spec.get("position", [0, 4, 0]))
		var rgb: Vector3 = _vec3(spec.get("color", [1.0, 0.69, 0.39]))
		light.light_color = Color(rgb.x, rgb.y, rgb.z)
		light.light_energy = float(spec.get("energy", 0.8))
		light.omni_range = float(spec.get("range", 5.0))
		light.omni_attenuation = float(spec.get("attenuation", 1.4))
		light.shadow_enabled = bool(spec.get("shadows", false))
		$PracticalLights.add_child(light)
		practical_profile.street_lights += 1
	_build_interior_practicals(profile)


func _build_interior_practicals(profile: Dictionary) -> void:
	# Authored candidates sit inside real window cavities. Small unshadowed
	# bulbs reveal nearby furniture without acting as exterior fill lights.
	var maximum: int = clampi(int(profile.get("interior_light_limit", 0)), 0, 12)
	if maximum == 0 or not FileAccess.file_exists("res://assets/architecture_manifest.json"):
		return
	var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/architecture_manifest.json"))
	if not manifest is Dictionary:
		return
	var candidates: Array = manifest.get("interior_lights", [])
	practical_profile.interior_candidate_count = candidates.size()
	for spec in candidates:
		if practical_profile.interior_lights.size() >= maximum:
			break
		if not spec is Dictionary or not spec.get("position", null) is Array:
			continue
		var light: OmniLight3D = OmniLight3D.new()
		light.name = str(spec.get("name", "InteriorPractical"))
		light.position = _vec3(spec.position)
		var rgb: Vector3 = _vec3(spec.get("color", [1.0, 0.89, 0.74]))
		light.light_color = Color(rgb.x, rgb.y, rgb.z)
		light.light_energy = clampf(float(spec.get("energy", 0.24)), 0.0, 0.32) * float(profile.get("interior_light_energy_scale", 1.0))
		light.light_specular = 0.25
		light.omni_range = clampf(float(spec.get("range", 2.8)), 0.5, 3.2)
		light.omni_attenuation = float(spec.get("attenuation", 1.5))
		light.shadow_enabled = false
		$PracticalLights.add_child(light)
		practical_profile.interior_lights.append({"name": light.name, "position": _array(light.position), "energy": light.light_energy, "range": light.omni_range, "shadows": false})
	print("CQ_INTERIOR_LIGHTS ", JSON.stringify(practical_profile))


func _configure_materials(node: Node) -> void:
	if node is MeshInstance3D:
		var mesh_instance: MeshInstance3D = node as MeshInstance3D
		if bool(gi_profile.enabled):
			if bool(gi_profile.structures_only) and not _is_primary_gi_structure(mesh_instance):
				mesh_instance.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
				material_stats.gi_excluded_meshes += 1
			else:
				mesh_instance.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		if mesh_instance.gi_mode == GeometryInstance3D.GI_MODE_STATIC:
			material_stats.static_gi_meshes += 1
		if str(node.name).begins_with("COL_Street_Paving"):
			mesh_instance.lod_bias = 4.0
		if mesh_instance.mesh != null:
			for surface in range(mesh_instance.mesh.get_surface_count()):
				var material: Material = mesh_instance.get_active_material(surface)
				if material is BaseMaterial3D:
					material_stats.surfaces += 1
					if (mesh_instance.mesh.surface_get_format(surface) & Mesh.ARRAY_FORMAT_COLOR) != 0:
						material.vertex_color_use_as_albedo = true
						material_stats.vertex_color_surfaces += 1
					material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
					# Preserve authored PBR maps; only architectural glass gets a
					# thin-sheet shader paired with the real recessed interiors.
					var material_name: String = material.resource_name.to_lower()
					if material_name.begins_with("cq_ph_island_tree_01") or material_name.begins_with("cq_ph_tree_small_02"):
						mesh_instance.lod_bias = float(art_profile.get("materials", {}).get("ph_tree_lod_bias", 1.0))
						if "branches" in material_name and bool(art_profile.get("materials", {}).get("ph_branch_shader", false)):
							mesh_instance.set_surface_override_material(surface, _branch_material(material))
							material_stats["explicit_branch_surfaces"] = int(material_stats.get("explicit_branch_surfaces", 0)) + 1
						if "leaves" in material_name and bool(art_profile.get("materials", {}).get("ph_leaf_safe_material", false)):
							mesh_instance.set_surface_override_material(surface, _safe_leaf_material(material))
							material_stats["safe_leaf_surfaces"] = int(material_stats.get("safe_leaf_surfaces", 0)) + 1
					if (material_name.begins_with("cq_ph_island_tree_01") or material_name.begins_with("cq_ph_tree_small_02")) and not bool(art_profile.get("materials", {}).get("ph_tree_normals", true)):
						material.normal_enabled = false
						if not material_stats.has("tree_normal_overrides"):
							material_stats["tree_normal_overrides"] = {}
						material_stats.tree_normal_overrides[material.resource_name] = "normal texture disabled; albedo/roughness/geometry preserved"
					if material_name.begins_with("cq03_pbr_tile"):
						if "--qa-no-tile-normal" in OS.get_cmdline_user_args():
							material.normal_enabled = false
						if "--qa-unshaded-tile" in OS.get_cmdline_user_args():
							material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
						if "--qa-no-tile-normal" in OS.get_cmdline_user_args() or "--qa-unshaded-tile" in OS.get_cmdline_user_args():
							material_stats.tile_diagnostics[material.resource_name] = {"normal_enabled": material.normal_enabled, "shading_mode": material.shading_mode}
					var architectural_mesh: bool = str(mesh_instance.name).begins_with("B_") or str(mesh_instance.name).begins_with("IR_B_")
					if architectural_mesh and ("glass" in material_name or material_name == "cqf_window") and bool(art_profile.get("materials", {}).get("thin_window_glass", false)):
						mesh_instance.set_surface_override_material(surface, _window_glass_material(material_name))
						material_stats["thin_glass_surfaces"] = int(material_stats.get("thin_glass_surfaces", 0)) + 1
					if material.resource_name == "CQ_PBR_tile":
						material.albedo_color = Color(0.88, 0.94, 1.0, 1.0)
					elif material.resource_name == "CQ_PBR_pavement":
						material.albedo_color = Color(0.88, 0.93, 0.98, 1.0)
	for child in node.get_children():
		_configure_materials(child)


func _safe_leaf_material(original: BaseMaterial3D) -> StandardMaterial3D:
	var key: String = original.resource_name
	if safe_leaf_materials.has(key):
		return safe_leaf_materials[key]
	var result: StandardMaterial3D = StandardMaterial3D.new()
	result.resource_name = "CQ04_SafeLeaf_" + key
	if bool(art_profile.get("materials", {}).get("ph_leaf_unshaded", false)):
		result.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	if bool(art_profile.get("materials", {}).get("ph_leaf_texture_diagnostics", false)):
		_record_leaf_texture(original)
	result.albedo_texture = original.albedo_texture
	result.albedo_color = original.albedo_color
	result.uv1_scale = original.uv1_scale
	result.uv1_offset = original.uv1_offset
	result.roughness = 0.85
	result.metallic = 0.0
	result.metallic_specular = 0.0
	result.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	result.normal_enabled = false
	result.ao_enabled = false
	result.vertex_color_use_as_albedo = false
	result.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
	result.cull_mode = BaseMaterial3D.CULL_DISABLED
	result.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	safe_leaf_materials[key] = result
	return result


func _record_leaf_texture(material: BaseMaterial3D) -> void:
	if not material_stats.has("leaf_texture_diagnostics"):
		material_stats["leaf_texture_diagnostics"] = {}
	var details: Dictionary = {"material": material.resource_name, "albedo_color": [material.albedo_color.r, material.albedo_color.g, material.albedo_color.b, material.albedo_color.a], "uv1_scale": _array(material.uv1_scale), "uv1_offset": _array(material.uv1_offset)}
	var texture: Texture2D = material.albedo_texture
	if texture != null:
		details["resource_path"] = texture.resource_path
		details["texture_class"] = texture.get_class()
		var source_image: Image = texture.get_image()
		if source_image != null and not source_image.is_empty():
			details["size"] = [source_image.get_width(), source_image.get_height()]
			details["format"] = source_image.get_format()
			if source_image.is_compressed():
				details["decompress_error"] = source_image.decompress()
			var total: Vector3 = Vector3.ZERO
			var lower: Vector3 = Vector3.ONE
			var upper: Vector3 = Vector3.ZERO
			var dark: int = 0
			var count: int = 0
			for y in range(0, source_image.get_height(), maxi(1, source_image.get_height() / 64)):
				for x in range(0, source_image.get_width(), maxi(1, source_image.get_width() / 64)):
					var pixel: Color = source_image.get_pixel(x, y)
					var rgb: Vector3 = Vector3(pixel.r, pixel.g, pixel.b)
					total += rgb
					lower = lower.min(rgb)
					upper = upper.max(rgb)
					count += 1
					if rgb.x + rgb.y + rgb.z < 0.03:
						dark += 1
			details["sample_count"] = count
			details["sample_rgb_mean"] = _array(total / maxf(1.0, count))
			details["sample_rgb_min"] = _array(lower)
			details["sample_rgb_max"] = _array(upper)
			details["sample_black_fraction"] = float(dark) / maxf(1.0, count)
	material_stats.leaf_texture_diagnostics[material.resource_name] = details
	print("CQ_LEAF_TEXTURE ", JSON.stringify(details))


func _branch_material(original: BaseMaterial3D) -> ShaderMaterial:
	var key: String = original.resource_name
	if branch_materials.has(key):
		return branch_materials[key]
	var result: ShaderMaterial = ShaderMaterial.new()
	result.shader = load("res://shaders/cq04_tree_bark.gdshader") as Shader
	result.resource_name = "CQ04_ExplicitBark_" + key
	result.set_shader_parameter("bark_albedo", original.albedo_texture)
	result.set_shader_parameter("bark_tint", original.albedo_color)
	var baked_primary: bool = bool(art_profile.get("materials", {}).get("ph_branch_uv_baked", false))
	var secondary_uv: bool = "tree_small_02" in key.to_lower() and not baked_primary
	# R5/R6 preserve the GLB's KHR_texture_transform and secondary UVs.
	# R7 bakes these into the primary UV in Blender and samples identity here.
	var uv_scale: Vector2 = Vector2.ONE if baked_primary else (Vector2(3.0, 0.5999999) if secondary_uv else Vector2(15.0, 3.4000001))
	var uv_offset: Vector2 = Vector2.ZERO if baked_primary else (Vector2(0.0, 0.4000001) if secondary_uv else Vector2(0.0, -2.4000001))
	result.set_shader_parameter("use_secondary_uv", secondary_uv)
	result.set_shader_parameter("bark_uv_scale", uv_scale)
	result.set_shader_parameter("bark_uv_offset", uv_offset)
	if not material_stats.has("branch_shader_overrides"):
		material_stats["branch_shader_overrides"] = {}
	material_stats.branch_shader_overrides[key] = {"texture": original.albedo_texture.resource_path if original.albedo_texture != null else "", "texcoord": 1 if secondary_uv else 0, "scale": [uv_scale.x, uv_scale.y], "offset": [uv_offset.x, uv_offset.y], "baked_primary": baked_primary, "imported_uv1_scale": _array(original.uv1_scale), "imported_uv1_offset": _array(original.uv1_offset), "imported_uv2_scale": _array(original.uv2_scale), "imported_uv2_offset": _array(original.uv2_offset), "normal_and_pbr_textures": false}
	print("CQ_BRANCH_OVERRIDE ", JSON.stringify(material_stats.branch_shader_overrides[key]))
	branch_materials[key] = result
	return result


func _window_glass_material(material_name: String) -> ShaderMaterial:
	if glass_materials.has(material_name):
		return glass_materials[material_name]
	var result: ShaderMaterial = ShaderMaterial.new()
	result.shader = load("res://shaders/cq04_window_glass.gdshader") as Shader
	result.resource_name = "CQ04_ThinWindowGlass_" + material_name
	var tint: Color = Color(0.18, 0.25, 0.27)
	if "warm" in material_name:
		tint = Color(0.28, 0.25, 0.17)
	elif "blue" in material_name:
		tint = Color(0.12, 0.20, 0.23)
	var settings: Dictionary = art_profile.get("materials", {})
	result.set_shader_parameter("glass_tint", tint)
	result.set_shader_parameter("base_opacity", float(settings.get("glass_opacity", 0.22)))
	result.set_shader_parameter("base_roughness", float(settings.get("glass_roughness", 0.23)))
	result.set_shader_parameter("grime_strength", float(settings.get("glass_grime_strength", 0.12)))
	glass_materials[material_name] = result
	return result


func _build_reflection_probes() -> void:
	var settings: Dictionary = art_profile.get("reflections", {})
	var enabled: bool = bool(settings.get("enabled", false)) and DisplayServer.get_name() != "headless" and RenderingServer.get_current_rendering_method() == "forward_plus"
	reflection_profile = {"enabled":enabled, "probes":[]}
	if not enabled:
		return
	for spec in settings.get("probes", []):
		var probe: ReflectionProbe = ReflectionProbe.new()
		probe.name = str(spec.get("name", "StreetReflection"))
		probe.position = _vec3(spec.get("position", [0,20,0]))
		probe.size = _vec3(spec.get("size", [120,70,120]))
		probe.origin_offset = _vec3(spec.get("origin_offset", [0,0,0]))
		probe.max_distance = float(spec.get("max_distance", 100))
		probe.intensity = float(spec.get("intensity", 0.75))
		probe.box_projection = true
		probe.ambient_mode = ReflectionProbe.AMBIENT_DISABLED
		probe.update_mode = ReflectionProbe.UPDATE_ONCE
		add_child(probe)
		reflection_profile.probes.append({"name":probe.name,"position":_array(probe.position),"size":_array(probe.size),"intensity":probe.intensity,"box_projection":true})


func _is_primary_gi_structure(mesh_instance: MeshInstance3D) -> bool:
	var mesh_name: String = str(mesh_instance.name)
	var primary: bool = mesh_name.begins_with("COL_") or mesh_name.begins_with("Context_") or mesh_name.begins_with("Outer_ground_context") or mesh_name.begins_with("Bridge_structure")
	if not primary or "Handrails" in mesh_name or mesh_name.begins_with("Context_windows") or mesh_name.ends_with("_frame") or "line_white" in mesh_name or mesh_instance.mesh == null:
		return false
	for surface in range(mesh_instance.mesh.get_surface_count()):
		var material: Material = mesh_instance.get_active_material(surface)
		if material is BaseMaterial3D:
			var material_name: String = material.resource_name.to_lower()
			if material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or "glass" in material_name or "leaf" in material_name:
				return false
	return true


func _update_camera_shadow_range() -> void:
	# Share the same height-based coverage in free exploration and native captures.
	# Historical profiles without this flag retain their fixed shadow distance.
	if not bool(applied_lighting.get("high_camera_shadow_range_enabled", false)) or not is_instance_valid(explorer):
		return
	var normal_distance: float = float(applied_lighting.get("shadow_max_distance", applied_lighting.get("shadow_distance", 180.0)))
	var height_threshold: float = float(applied_lighting.get("high_camera_shadow_height_m", 80.0))
	var high_distance: float = float(applied_lighting.get("high_camera_shadow_max_distance", 450.0))
	var target_distance: float = high_distance if explorer.camera.global_position.y > height_threshold else normal_distance
	if not is_equal_approx($Sun.directional_shadow_max_distance, target_distance):
		$Sun.directional_shadow_max_distance = target_distance
		print("CQ_CAMERA_SHADOW_RANGE ", JSON.stringify(_directional_shadow_state()))


func _directional_shadow_state() -> Dictionary:
	var distance_m: float = $Sun.directional_shadow_max_distance
	return {
		"max_distance_m": distance_m,
		"mode": $Sun.directional_shadow_mode,
		"split_fractions": [$Sun.directional_shadow_split_1, $Sun.directional_shadow_split_2, $Sun.directional_shadow_split_3],
		"fade_start_fraction": $Sun.directional_shadow_fade_start,
		"fade_start_distance_m": distance_m * $Sun.directional_shadow_fade_start,
		"blend_splits": $Sun.directional_shadow_blend_splits,
		"camera_world_y_m": explorer.camera.global_position.y if is_instance_valid(explorer) else null,
		"high_camera_policy_enabled": bool(applied_lighting.get("high_camera_shadow_range_enabled", false))
	}


func _process(delta: float) -> void:
	_toast_remaining = maxf(0.0, _toast_remaining - delta)
	_elapsed += delta
	if _elapsed < 0.15 or not is_instance_valid(explorer):
		return
	_elapsed = 0.0
	_update_camera_shadow_range()
	explorer.camera.near = 0.8 if explorer.camera.global_position.y > 80.0 else 0.08
	if is_instance_valid(gameplay):
		var status: Dictionary = gameplay.ui()
		if gameplay.passage and gameplay.passage.stage!=gameplay.passage.Stage.IDLE:
			mode_label.text="自主配送   /   穿楼托送"
			controls_label.text=gameplay.lesson.controls()
		elif gameplay.lunch and gameplay.lunch.active:
			mode_label.text = "自主配送   /   午市"
			controls_label.text = ("W S 加减速　A D 转向　空格刹车　P 停车　E 下车" if gameplay.riding() else "W A S D 走路　鼠标转头　Shift 快跑　E 交互")+"\nV 翻小票　超时每单少 3 元"
		elif gameplay.lesson and not explorer.review_shortcuts:
			controls_label.text = gameplay.lesson.controls()
			mode_label.text = "入职带教   /   第一班"
		objective_label.text = status.objective
		prompt_label.text = status.prompt
		prompt_label.visible = explorer.walking and not str(status.prompt).is_empty()
		mode_button.disabled = gameplay.riding()
		return
	var foot: Vector3 = explorer.body.global_position
	var destination: Vector3 = _pickup if _delivery_stage == 0 else _dropoff
	var distance: float = foot.distance_to(destination)
	if _delivery_stage == 0:
		objective_label.text = "第一单 · %s\n到店取餐   %d m" % [str(config.get("pickup_label", "山城小面")), roundi(distance)]
	elif _delivery_stage == 1:
		objective_label.text = "配送中 · %s\n沿坡道或楼梯上行   %d m" % [str(config.get("dropoff_label", "上层住宅入口")), roundi(distance)]
	else:
		objective_label.text = "订单已送达\n继续走走，看看这条街巷"
	if _toast_remaining <= 0.0:
		prompt_label.visible = explorer.walking and _delivery_stage < 2 and distance <= 3.2
		prompt_label.text = "E  取餐" if _delivery_stage == 0 else "E  送达"


func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.physical_keycode:
		KEY_H:
			hud.visible = not hud.visible
			get_viewport().set_input_as_handled()
		KEY_F12:
			_save_current_view()
			get_viewport().set_input_as_handled()
		KEY_E:
			if is_instance_valid(explorer) and explorer.walking:
				_interact()
				get_viewport().set_input_as_handled()


func _interact() -> void:
	if is_instance_valid(gameplay):
		gameplay.interact()
		return
	if _delivery_stage >= 2:
		return
	var destination: Vector3 = _pickup if _delivery_stage == 0 else _dropoff
	if explorer.body.global_position.distance_to(destination) > 3.2:
		return
	_delivery_stage += 1
	prompt_label.text = "已取餐 · 送往上层住宅入口" if _delivery_stage == 1 else "已送达 · 谢谢，辛苦了！"
	prompt_label.visible = true
	_toast_remaining = 3.0


func _save_current_view() -> void:
	if not is_instance_valid(explorer):
		return
	await RenderingServer.frame_post_draw
	var folder: String = "user://screenshots"
	DirAccess.make_dir_recursive_absolute(folder)
	var filename: String = "chongqing_%s_%d.png" % [explorer.current_view, int(Time.get_unix_time_from_system())]
	var path: String = folder.path_join(filename)
	var err: Error = get_viewport().get_texture().get_image().save_png(path)
	print("CQ_SCREENSHOT ", ProjectSettings.globalize_path(path), " result=", err)
	prompt_label.visible = true
	prompt_label.text = "截图已保存" if err == OK else "截图保存失败"
	_toast_remaining = 2.0


func _mode_changed(walking: bool) -> void:
	mode_button.text = "Tab  自由观察" if walking else "Tab  落地步行"
	var dimension := "500 × 500" if district_500_enabled else "200 × 200"
	mode_label.text = "%s   /   %s 米街区" % ["步行探索" if walking else "自由观察", dimension]
	controls_label.text = "W A S D 移动    鼠标转向    Esc 释放    Shift 快跑    空格跳跃    E 交互\nR 回到街口    1–0 固定机位   [ / ] 切换    Tab 自由观察    H 隐藏界面    F12 截图" if walking else "W A S D 移动    单击场景后鼠标转向    Esc 释放    Q 下降 / E 上升    Shift 加速    滚轮缩放\n1–0 固定机位   [ / ] 切换    Tab 落地步行    H 隐藏界面    F12 截图"


func _view(view_name: String) -> void:
	if is_instance_valid(gameplay) and gameplay.riding():
		return
	if is_instance_valid(explorer):
		explorer.go_to_view(view_name)


func _toggle_mode() -> void:
	if is_instance_valid(gameplay) and gameplay.riding():
		return
	if is_instance_valid(explorer):
		explorer.set_mode(not explorer.walking)


func _build_hud() -> void:
	var layer: CanvasLayer = CanvasLayer.new()
	layer.name = "Interface"
	add_child(layer)
	hud = Control.new()
	hud.name = "HUD"
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(hud)
	var theme: Theme = Theme.new()
	theme.default_font = UI_FONT
	theme.default_font_size = 15
	hud.theme = theme

	var title_panel: PanelContainer = _panel(Vector2(26, 24), Vector2(365, 92))
	var title_stack: VBoxContainer = VBoxContainer.new()
	title_stack.add_theme_constant_override("separation", 6)
	title_panel.add_child(title_stack)
	title_stack.add_child(_label("梯坎里 · 重庆", 26, Color("eef0e8")))
	mode_label = _label("步行探索", 13, Color("aebdbb"))
	title_stack.add_child(mode_label)

	var objective_panel: PanelContainer = _panel(Vector2(26, 128), Vector2(325, 80))
	objective_label = _label("第一单 · 山城小面", 15, Color("ead0a0"))
	objective_label.add_theme_constant_override("line_spacing", 7)
	objective_panel.add_child(objective_label)

	var nav: HBoxContainer = HBoxContainer.new()
	nav.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	nav.position = Vector2(-646, 26)
	nav.add_theme_constant_override("separation", 7)
	hud.add_child(nav)
	view_picker = OptionButton.new()
	view_picker.custom_minimum_size = Vector2(238, 38)
	view_picker.focus_mode = Control.FOCUS_NONE
	for i in range(VIEW_NAMES.size()):
		var info: Dictionary = config.views[VIEW_NAMES[i]]
		view_picker.add_item("%02d  %s" % [i + 1, str(info.get("title", VIEW_NAMES[i]))])
	view_picker.item_selected.connect(func(index: int): _view(VIEW_NAMES[index]))
	nav.add_child(view_picker)
	var previous: Button = _button("[ 上一处")
	previous.pressed.connect(func(): explorer.cycle_view(-1))
	nav.add_child(previous)
	var next: Button = _button("] 下一处")
	next.pressed.connect(func(): explorer.cycle_view(1))
	nav.add_child(next)
	mode_button = _button("Tab 自由观察")
	mode_button.pressed.connect(_toggle_mode)
	nav.add_child(mode_button)

	var help: PanelContainer = PanelContainer.new()
	help.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	help.offset_left = 26
	help.offset_top = -118
	help.offset_right = 828
	help.offset_bottom = -42
	help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	help.add_theme_stylebox_override("panel", _panel_style())
	hud.add_child(help)
	controls_label = _label("", 13, Color("d5ded7"))
	controls_label.add_theme_constant_override("line_spacing", 7)
	help.add_child(controls_label)

	prompt_label = _label("", 20, Color("f7e4b9"))
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	prompt_label.offset_left = -300
	prompt_label.offset_right = 300
	prompt_label.offset_top = -183
	prompt_label.offset_bottom = -143
	prompt_label.visible = false
	hud.add_child(prompt_label)

	var credit: Label = _label("© OpenStreetMap contributors · 基础平面源自 OSM；建筑外观与高程为参考设计，非测绘复刻", 11, Color("bcc9c5"))
	if art_profile.get("river_r22",false):
		credit.text="© OpenStreetMap contributors · ODbL 1.0 · openstreetmap.org/copyright · 建筑外观及高程为美术设计"
	credit.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	credit.offset_left = 30
	credit.offset_top = -27
	credit.offset_right = 1300
	credit.offset_bottom = -9
	hud.add_child(credit)


func _panel(position_: Vector2, size_: Vector2) -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()
	panel.position = position_
	panel.size = size_
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_theme_stylebox_override("panel", _panel_style())
	hud.add_child(panel)
	return panel


func _label(text_: String, font_size: int, color: Color) -> Label:
	var label: Label = Label.new()
	label.text = text_
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_shadow_color", Color(0.01, 0.03, 0.03, 0.8))
	label.add_theme_constant_override("shadow_offset_y", 1)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _button(text_: String) -> Button:
	var button: Button = Button.new()
	button.text = text_
	button.custom_minimum_size = Vector2(94, 38)
	button.focus_mode = Control.FOCUS_NONE
	button.add_theme_font_size_override("font_size", 14)
	button.add_theme_color_override("font_color", Color("e6ece6"))
	var normal: StyleBoxFlat = _panel_style()
	normal.content_margin_left = 12
	normal.content_margin_right = 12
	normal.content_margin_top = 8
	normal.content_margin_bottom = 8
	button.add_theme_stylebox_override("normal", normal)
	var hover: StyleBoxFlat = normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(0.18, 0.26, 0.25, 0.95)
	button.add_theme_stylebox_override("hover", hover)
	return button


func _panel_style() -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color(0.035, 0.07, 0.07, 0.78)
	style.set_corner_radius_all(4)
	style.content_margin_left = 18
	style.content_margin_right = 18
	style.content_margin_top = 12
	style.content_margin_bottom = 12
	return style


func _run_smoke_test(survey_mode: bool = false) -> void:
	var report: Dictionary = {"engine": Engine.get_version_info().string, "collision_stats": collision_stats, "sample_adjustments": survey_sample_adjustments, "tests": []}
	report["scene_identity"] = scene_identity
	report["scene_sha256"] = scene_identity.get("sha256", "")
	report["scene_revision"] = scene_identity.get("revision", null)
	report["gi_profile"] = gi_profile
	report["controller"] = {"version": "swept_step_landing_v2", "step_height_m": ExplorerScript.STEP_HEIGHT, "maximum_landing_probe_m": 0.35, "waypoints_teleport": false, "step_validation": "Upward headroom, horizontal sweep, downward walkable landing; shortest safe landing is chosen"}
	var script_fingerprints: Dictionary = {}
	for path in ["res://scripts/main.gd", "res://scripts/explorer.gd", "res://scripts/build_collisions.gd"]:
		script_fingerprints[path] = FileAccess.get_file_as_string(path).sha256_text()
	report["script_sha256"] = script_fingerprints
	report["configuration_sha256"] = {
		"res://assets/viewpoints.json": FileAccess.get_sha256("res://assets/viewpoints.json"),
		"res://assets/walking_survey.json": FileAccess.get_sha256("res://assets/walking_survey.json")
	}
	var tests: Array = report.tests
	tests.append({"name": "world_collision_created", "pass": int(collision_stats.bodies) > 0 and collision_stats.failed.is_empty()})
	for view_name in VIEW_NAMES:
		explorer.go_to_view(view_name)
		var p: Vector3 = explorer.camera.global_position
		tests.append({"name": "camera_" + view_name, "pass": p.is_finite(), "position": _array(p)})
	explorer.go_to_view("walk")
	for i in range(120):
		await get_tree().physics_frame
	var foot: Vector3 = explorer.body.global_position
	var configured: Vector3 = _vec3(config.walk_spawn)
	tests.append({"name": "walk_spawn_stands_on_ground", "pass": explorer.body.is_on_floor() and foot.distance_to(configured) < 1.0, "foot_position": _array(foot)})
	for value in config.get("ground_samples", []):
		var from: Vector3 = _vec3(value)
		var hit: Dictionary = CollisionBuilder.raycast_ground(self, from, 8)
		tests.append({"name": "ground_probe", "from": _array(from), "pass": not hit.is_empty() and (hit.normal as Vector3).y > 0.65})
	for value in config.get("wall_tests", []):
		var query: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(_vec3(value.from), _vec3(value.to), 1)
		var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(query)
		tests.append({"name": str(value.get("name", "wall_blocks_ray")), "pass": not hit.is_empty()})
	var routes: Array = config.get("walking_tests", []).duplicate(true)
	if survey_mode and FileAccess.file_exists("res://assets/walking_survey.json"):
		var supplemental: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/walking_survey.json"))
		if supplemental is Dictionary:
			routes.append_array(supplemental.get("routes", []))
	var route_filter: PackedStringArray = []
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--route-only="):
			route_filter = arg.trim_prefix("--route-only=").split(",", false)
	report["route_filter"] = Array(route_filter)
	report["configured_route_count"] = routes.size()
	var tested_route_names: Array[String] = []
	for route in routes:
		if not route_filter.is_empty() and not route_filter.has(str(route.get("name", ""))):
			continue
		tested_route_names.append(str(route.get("name", "")))
		tests.append(await _test_walking_route(route))
	if not route_filter.is_empty():
		for selected in route_filter:
			tests.append({"name": "requested_route_exists_" + selected, "pass": tested_route_names.has(selected)})
	report["tested_route_names"] = tested_route_names
	_delivery_stage = 0
	explorer.body.global_position = _pickup + Vector3(0, 0, 10)
	await get_tree().physics_frame
	_interact()
	tests.append({"name": "pickup_requires_proximity", "pass": _delivery_stage == 0})
	explorer.body.global_position = _pickup + Vector3(0.6, 0.1, 0)
	await get_tree().physics_frame
	await get_tree().physics_frame
	_interact()
	# R18 packing is a complete 3.2-second performance. The old 110-frame
	# assumption predates it; wait for the real READY state with a hard timeout.
	for frame in range(300):
		if is_instance_valid(gameplay) and gameplay.order == 2:
			break
		await get_tree().physics_frame
	tests.append({"name": "preparation_completes_before_timeout", "pass": is_instance_valid(gameplay) and gameplay.order == 2})
	_interact()
	tests.append({"name": "pickup_advances_order", "pass": _delivery_stage == 1})
	_interact()
	tests.append({"name": "cannot_deliver_at_pickup", "pass": _delivery_stage == 1})
	explorer.set_walk_origin(Vector3(-63.84,19.94,19.65),gameplay.destination.global_position)
	for frame in 12:await get_tree().physics_frame
	_interact()
	tests.append({"name":"upstairs_resident_confirms","pass":gameplay.free_answered and _delivery_stage==1})
	explorer.set_walk_origin(Vector3(-63.77,19.94,20.27),gameplay.destination.global_position)
	for frame in 12:await get_tree().physics_frame
	_interact()
	for frame in 90:await get_tree().physics_frame
	tests.append({"name": "dropoff_completes_order", "pass": _delivery_stage == 2})
	_interact()
	tests.append({"name": "completed_order_idempotent", "pass": _delivery_stage == 2})
	if survey_mode:
		_append_survey_checks(tests, report)
	var all_passed: bool = true
	for test in tests:
		all_passed = all_passed and bool(test["pass"])
	report["passed"] = all_passed
	preload("res://scripts/qa_context.gd").decorate(report, self)
	var output_name: String = "godot_survey_test.json" if survey_mode else "godot_smoke_test.json"
	var output_path: String = preload("res://scripts/qa_context.gd").directory("res://verification").path_join(output_name)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--test-report="):
			output_path = arg.trim_prefix("--test-report=")
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var out: FileAccess = FileAccess.open(output_path, FileAccess.WRITE)
	if out:
		out.store_string(JSON.stringify(report, "\t"))
	print("CQ_SURVEY " if survey_mode else "CQ_SMOKE ", JSON.stringify(report))
	get_tree().quit(0 if all_passed else 2)


func _test_walking_route(route: Dictionary) -> Dictionary:
	var from: Vector3 = _vec3(route.from)
	var to: Vector3 = _vec3(route.to)
	var goals: Array[Vector3] = []
	for point in route.get("waypoints", []):
		goals.append(_vec3(point))
	goals.append(to)
	explorer.begin_route_test(from, goals[0])
	for i in range(45):
		await get_tree().physics_frame
	var start: Vector3 = explorer.body.global_position
	var previous: Vector3 = start
	var goal_index: int = 0
	var trajectory_length: float = 0.0
	var max_displacement: float = 0.0
	var used_frames: int = 0
	var minimum_y: float = start.y
	var reached: Array = []
	var last_stall_contacts: Array = []
	explorer.automation_axis = Vector2(0.0, -1.0)
	for i in range(int(route.get("frames", 420))):
		explorer.aim_route_test(goals[goal_index])
		await get_tree().physics_frame
		used_frames = i + 1
		var position_: Vector3 = explorer.body.global_position
		if Vector2(position_.x - previous.x, position_.z - previous.z).length() < 0.005:
			last_stall_contacts.clear()
			for index in range(explorer.body.get_slide_collision_count()):
				var contact: KinematicCollision3D = explorer.body.get_slide_collision(index)
				var collider: Node = contact.get_collider() as Node
				last_stall_contacts.append({"collider": str(collider.get_parent().name) if is_instance_valid(collider) else "unknown", "normal": _array(contact.get_normal()), "position": _array(contact.get_position())})
		max_displacement = maxf(max_displacement, position_.distance_to(previous))
		trajectory_length += Vector2(position_.x - previous.x, position_.z - previous.z).length()
		minimum_y = minf(minimum_y, position_.y)
		previous = position_
		var goal: Vector3 = goals[goal_index]
		if Vector2(goal.x - position_.x, goal.z - position_.z).length() <= 0.35:
			reached.append({"index": goal_index, "foot": _array(position_)})
			goal_index += 1
			if goal_index == goals.size():
				break
	explorer.end_route_test()
	for i in range(30):
		await get_tree().physics_frame
	var end: Vector3 = explorer.body.global_position
	var horizontal: float = Vector2(end.x - start.x, end.z - start.z).length()
	var gain: float = end.y - start.y
	var goal_distance: float = Vector2(end.x - to.x, end.z - to.z).length()
	var expected_y: float = float(route.get("expected_end_height", end.y))
	var height_ok: bool = absf(end.y - expected_y) <= float(route.get("height_tolerance", 0.35))
	var route_ok: bool = horizontal >= float(route.get("min_progress_m", 1.0)) and gain >= float(route.get("min_height_gain_m", 0.0)) and explorer.body.is_on_floor() and goal_distance <= 1.2 and goal_index == goals.size() and height_ok and max_displacement < 1.0
	var result: Dictionary = {"name": str(route.get("name", "walking_route")), "pass": route_ok, "from": _array(start), "to": _array(end), "horizontal_progress_m": horizontal, "height_gain_m": gain, "goal_distance_m": goal_distance, "on_floor": explorer.body.is_on_floor(), "goals_reached": reached, "goals_total": goals.size(), "trajectory_length_m": trajectory_length, "max_frame_displacement_m": max_displacement, "minimum_foot_height_m": minimum_y, "frames": used_frames, "continuous_controller_walk": true}
	if not route_ok:
		result["last_stall_contacts"] = last_stall_contacts
	var final_floor: Dictionary = CollisionBuilder.raycast_ground(self, end + Vector3.UP * 0.20, 1.0)
	if not final_floor.is_empty():
		result["end_floor"] = str((final_floor.collider as Node).get_parent().name)
	if route.has("expected_end_height"):
		result["expected_end_height"] = expected_y
		result["end_height_matches"] = height_ok
	print("CQ_WALK_TEST ", JSON.stringify(result))
	return result


func _capture_views() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Capture requires a rendering display; --headless is for physics verification only.")
		get_tree().quit(3)
		return
	var output_dir: String = "res://verification"
	var selected_view: String = ""
	var settle_frames: int = 12
	var capture_size: Vector2i = Vector2i(1920, 1080)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture-dir="):
			output_dir = arg.trim_prefix("--capture-dir=")
		if arg.begins_with("--capture-view="):
			selected_view = arg.trim_prefix("--capture-view=")
		if arg.begins_with("--settle-frames="):
			settle_frames = maxi(3, int(arg.trim_prefix("--settle-frames=")))
		if arg.begins_with("--capture-size="):
			var size_args: PackedStringArray = arg.trim_prefix("--capture-size=").split("x")
			if size_args.size() == 2:
				capture_size = Vector2i(clampi(int(size_args[0]), 320, 4096), clampi(int(size_args[1]), 180, 2160))
	var selected_views: PackedStringArray = selected_view.split(",", false)
	if bool(gi_profile.enabled):
		settle_frames = maxi(settle_frames, 8)
	for selected in selected_views:
		if not VIEW_NAMES.has(selected):
			push_error("Unknown capture view: " + selected)
			get_tree().quit(3)
			return
	var capture_order: Array[String] = []
	if selected_views.is_empty():
		capture_order.assign(VIEW_NAMES)
	else:
		for selected in selected_views:
			if not capture_order.has(selected):
				capture_order.append(selected)
	DirAccess.make_dir_recursive_absolute(output_dir)
	hud.visible = false
	explorer.can_control(false)
	# An exact-size runtime viewport renders the same live World3D, independent
	# of the native desktop window size. The PNG is never resized or retouched.
	var capture_viewport: SubViewport = SubViewport.new()
	capture_viewport.name = "RuntimeCaptureViewport"
	capture_viewport.size = capture_size
	capture_viewport.world_3d = get_world_3d()
	capture_viewport.own_world_3d = false
	capture_viewport.msaa_3d = get_viewport().msaa_3d
	capture_viewport.screen_space_aa = get_viewport().screen_space_aa
	capture_viewport.use_taa = get_viewport().use_taa
	capture_viewport.use_occlusion_culling = get_viewport().use_occlusion_culling
	capture_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(capture_viewport)
	var capture_camera: Camera3D = Camera3D.new()
	capture_camera.name = "RuntimeCaptureCamera"
	capture_camera.far = explorer.camera.far
	capture_viewport.add_child(capture_camera)
	capture_camera.current = true
	# Display the render target on the native window while it is being captured.
	# Root 3D is disabled only to avoid rendering the city twice per frame.
	get_viewport().disable_3d = true
	var preview_layer: CanvasLayer = CanvasLayer.new()
	preview_layer.layer = 100
	add_child(preview_layer)
	var preview: TextureRect = TextureRect.new()
	preview.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	preview.texture = capture_viewport.get_texture()
	preview_layer.add_child(preview)
	var report: Dictionary = {
		"engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method(),
		"display_server": DisplayServer.get_name(),
		"captured_at_unix": Time.get_unix_time_from_system(),
		"source": "Exact-size Godot runtime SubViewport sharing the playable World3D; original PNG, no resizing or retouching",
		"requested_size": [capture_size.x, capture_size.y],
		"capture_order": capture_order,
		"scene": "res://assets/chongqing_district.glb",
		"scene_identity": scene_identity,
		"scene_sha256": scene_identity.get("sha256", ""),
		"scene_revision": scene_identity.get("revision", null),
		"character_sha256": FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),
		"character_import_sha256": FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import"),
		"counter_sha256": FileAccess.get_sha256("res://assets/characters/serving_counter_r18.glb"),
		"script_sha256": {
			"res://scripts/main.gd": FileAccess.get_sha256("res://scripts/main.gd"),
			"res://scripts/shopkeeper.gd": FileAccess.get_sha256("res://scripts/shopkeeper.gd"),
			"res://scripts/shopkeeper_attention.gd": FileAccess.get_sha256("res://scripts/shopkeeper_attention.gd"),
			"res://scripts/gameplay.gd": FileAccess.get_sha256("res://scripts/gameplay.gd"),
			"res://scripts/takeaway_bag.gd": FileAccess.get_sha256("res://scripts/takeaway_bag.gd"),
			"res://scripts/explorer.gd": FileAccess.get_sha256("res://scripts/explorer.gd"),
			"res://scripts/build_collisions.gd": FileAccess.get_sha256("res://scripts/build_collisions.gd")
		},
		"configuration_sha256": {
			"res://assets/viewpoints.json": FileAccess.get_sha256("res://assets/viewpoints.json"),
			"res://assets/walking_survey.json": FileAccess.get_sha256("res://assets/walking_survey.json")
		},
		"material_stats": material_stats,
		"sky_profile": sky_profile,
		"gi_profile": gi_profile,
		"art_profile": art_profile,
		"art_profile_path": art_profile_path,
		"art_profile_sha256": FileAccess.get_sha256(art_profile_path),
		"reflection_profile": reflection_profile,
		"practical_profile": practical_profile,
		"applied_lighting_profile": applied_lighting,
		"diagnostic_overrides": {"external_art_profile": art_profile_path != DEFAULT_ART_PROFILE, "tile_normal_disabled": "--qa-no-tile-normal" in OS.get_cmdline_user_args(), "tile_unshaded": "--qa-unshaded-tile" in OS.get_cmdline_user_args(), "sun_shadows_disabled": "--qa-no-sun-shadows" in OS.get_cmdline_user_args(), "sdfgi_experiment": _gi_qa_requested()},
		"render_effects": {"ssao": $WorldEnvironment.environment.ssao_enabled, "ssao_radius": $WorldEnvironment.environment.ssao_radius, "ssao_intensity": $WorldEnvironment.environment.ssao_intensity, "ssao_detail": $WorldEnvironment.environment.ssao_detail, "ssr": $WorldEnvironment.environment.ssr_enabled, "ssil": $WorldEnvironment.environment.ssil_enabled, "ssil_intensity": $WorldEnvironment.environment.ssil_intensity, "glow": $WorldEnvironment.environment.glow_enabled, "tonemap_mode": $WorldEnvironment.environment.tonemap_mode, "tonemap_exposure": $WorldEnvironment.environment.tonemap_exposure, "tonemap_white": $WorldEnvironment.environment.tonemap_white, "sdfgi": $WorldEnvironment.environment.sdfgi_enabled, "sdfgi_cascades": $WorldEnvironment.environment.sdfgi_cascades, "sdfgi_cell_metres": $WorldEnvironment.environment.sdfgi_min_cell_size, "sdfgi_read_sky": $WorldEnvironment.environment.sdfgi_read_sky_light},
		"lighting_applied_initial": {"sun_energy":$Sun.light_energy,"sun_specular":$Sun.light_specular,"sun_shadows":$Sun.shadow_enabled,"shadow_bias":$Sun.shadow_bias,"shadow_normal_bias":$Sun.shadow_normal_bias,"shadow_distance":$Sun.directional_shadow_max_distance,"ambient_energy":$WorldEnvironment.environment.ambient_light_energy,"ambient_source":$WorldEnvironment.environment.ambient_light_source,"sky_contribution":$WorldEnvironment.environment.ambient_light_sky_contribution,"reflection_source":$WorldEnvironment.environment.reflected_light_source},
		"captures": [],
		"failures": []
	}
	var device: RenderingDevice = RenderingServer.get_rendering_device()
	if device != null:
		report["device"] = device.get_device_name()
	for view_name in capture_order:
		var pose: Dictionary = config.views[view_name].get("capture_state",{})
		if is_instance_valid(gameplay.court_resident):
			gameplay.court_resident.pose(StringName(pose.get("resident_clip","sit_rest")),float(pose.get("resident_time",4.0)))
		if is_instance_valid(gameplay.rinse_tap):
			gameplay.rinse_tap.close()
			if pose.get("rinse_running",false):
				gameplay.rinse_tap.toggle()
		if is_instance_valid(gameplay.shopkeeper.animator):
			gameplay.shopkeeper.animator.stop()
			gameplay.shopkeeper.animator.play(gameplay.shopkeeper.available_clips.get(str(pose.get("character_clip","idle")),"idle"),0)
			gameplay.shopkeeper.animator.seek(float(pose.get("time",0)),true)
			gameplay.shopkeeper.animator.advance(0)
			gameplay.shopkeeper.animator.pause()
		gameplay.bag.visible=bool(pose.get("food_ready",false))
		gameplay.shopkeeper.set_smile(float(pose.get("smile",.035)))
		gameplay.shopkeeper.set_blink(float(pose.get("blink",0)))
		gameplay.shopkeeper.attention.tracking=bool(pose.get("look_at_camera",false))
		gameplay.shopkeeper.packing=str(pose.get("character_clip","idle"))=="serve"
		if gameplay.shopkeeper.packing:
			gameplay.shopkeeper.update_food_contact()
		else:
			gameplay.bag.global_position=gameplay.shopkeeper.food_end
		print("CQ_CAPTURE_START ", view_name, " after ", Time.get_ticks_msec() - startup_ms, " ms from startup")
		explorer.go_to_view(view_name)
		capture_camera.global_transform = explorer.camera.global_transform
		gameplay.shopkeeper.attention.target=capture_camera.global_position
		if bool(pose.get("look_at_food",false)):
			gameplay.shopkeeper.attention.tracking=true
			gameplay.shopkeeper.attention.target=gameplay.bag.global_position+Vector3.UP*gameplay.shopkeeper.HANDLE_HEIGHT
		explorer.camera.clear_current(false)
		get_viewport().disable_3d = true
		capture_camera.make_current()
		capture_camera.fov = explorer.camera.fov
		capture_camera.near = 0.4 if capture_camera.global_position.y > 80.0 else 0.06
		await get_tree().create_timer(0.4).timeout
		var started: int = Time.get_ticks_msec()
		for i in range(settle_frames):
			await RenderingServer.frame_post_draw
		var render_ms: int = Time.get_ticks_msec() - started
		var img: Image = capture_viewport.get_texture().get_image()
		if img == null or img.is_empty():
			report.failures.append({"view": view_name, "error": "Empty runtime viewport image"})
			push_error("Empty viewport image: " + view_name)
			continue
		var path: String = output_dir.path_join("godot_" + view_name + ".png")
		var exact_size: bool = img.get_width() == capture_size.x and img.get_height() == capture_size.y
		var err: Error = img.save_png(path)
		var capture: Dictionary = {
			"capture_state":pose,
			"rinse_visibly_running":is_instance_valid(gameplay.rinse_tap) and gameplay.rinse_tap.stream_mesh.visible,
			"view": view_name,
			"title": config.views[view_name].get("title", view_name),
			"path": path,
			"width": img.get_width(),
			"height": img.get_height(),
			"exact_requested_size": exact_size,
			"native_viewport_3d_disabled":get_viewport().disable_3d,
			"native_viewport_has_camera":get_viewport().get_camera_3d() != null,
			"capture_viewport_has_camera":capture_viewport.get_camera_3d() == capture_camera,
			"position": _array(capture_camera.global_position),
			"target": config.views[view_name].target,
			"fov": capture_camera.fov,
			"directional_shadow": _directional_shadow_state(),
			"save_error": err,
			"settle_frames": settle_frames,
			"settle_elapsed_ms": render_ms,
			"rendered_objects": Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
			"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			"rendered_primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
		}
		report.captures.append(capture)
		if err != OK or not exact_size:
			report.failures.append({"view": view_name, "error": "Save or resolution check failed"})
		print("CQ_CAPTURE ", JSON.stringify(capture))
	var out: FileAccess = FileAccess.open(output_dir.path_join("capture_manifest.json"), FileAccess.WRITE)
	if out:
		out.store_string(JSON.stringify(report, "\t"))
	else:
		report.failures.append({"error": "Cannot write capture manifest"})
	print("CQ_CAPTURE_FINISHED ", report.captures.size(), " views; errors=", report.failures.size())
	get_tree().quit(0 if report.failures.is_empty() else 3)


func _view_changed(view_name: String) -> void:
	_update_camera_shadow_range()
	var index: int = VIEW_NAMES.find(view_name)
	if index >= 0 and is_instance_valid(view_picker):
		view_picker.select(index)


func _append_survey_checks(tests: Array, report: Dictionary) -> void:
	# These grid rays verify collision surface coverage, including rooftops.
	# They are not assertions that every point is a walkable street.
	var grid: Array = []
	var grid_count: int = clampi(int(config.get("survey_grid_count", 11)), 3, 31)
	var bounds: Array = [-100.0, -100.0, 100.0, 100.0]
	var extent: Variant = config.get("survey_extent", bounds)
	if extent is Array and extent.size() == 4:
		bounds = extent
	elif extent is float or extent is int:
		var radius: float = absf(float(extent))
		bounds = [-radius, -radius, radius, radius]
	var inset: float = float(config.get("survey_grid_inset", 0.0))
	var top: float = float(config.get("survey_ray_top", 250.0))
	var valid: int = 0
	for row in range(grid_count):
		for column in range(grid_count):
			var x: float = lerpf(float(bounds[0]) + inset, float(bounds[2]) - inset, float(column) / float(grid_count - 1))
			var z: float = lerpf(float(bounds[1]) + inset, float(bounds[3]) - inset, float(row) / float(grid_count - 1))
			var hit: Dictionary = CollisionBuilder.raycast_ground(self, Vector3(x, top, z), top + 50.0)
			var ok: bool = not hit.is_empty()
			var entry: Dictionary = {"position_xz": [x, z], "pass": ok}
			if ok:
				valid += 1
				entry["surface"] = _array(hit.position)
				entry["normal"] = _array(hit.normal)
				entry["kind"] = (hit.collider as Node).get_meta("cq_collision_kind", "unknown")
			grid.append(entry)
	report["region_coverage"] = {"extent_xz_m": bounds, "grid": [grid_count, grid_count], "covered": valid, "samples": grid, "meaning": "Vertical collision coverage of terrain or roofs; does not imply street walkability"}
	tests.append({"name": "whole_region_vertical_surface_coverage", "pass": valid == grid_count * grid_count, "covered": valid, "total": grid_count * grid_count})
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = 0.30
	capsule.height = 1.75
	var clearances: Array = []
	var samples: Array = config.get("clearance_samples", config.get("ground_samples", [])).duplicate(true)
	if FileAccess.file_exists("res://assets/walking_survey.json"):
		var supplemental: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/walking_survey.json"))
		if supplemental is Dictionary:
			samples.append_array(supplemental.get("clearance_samples", []))
	for i in range(samples.size()):
		var sample: Vector3 = _vec3(samples[i])
		var hit: Dictionary = CollisionBuilder.raycast_ground(self, sample, 8.0)
		var entry: Dictionary = {"index": i, "sample": _array(sample), "pass": false}
		if hit.is_empty():
			entry["reason"] = "No ground below configured walking sample"
		else:
			var foot: Vector3 = hit.position
			var normal: Vector3 = hit.normal
			var contacts: Array[Dictionary] = _capsule_contacts(capsule, foot + Vector3.UP * 0.06)
			entry["foot"] = _array(foot)
			entry["normal"] = _array(normal)
			entry["initial_contacts"] = _contact_names(contacts)
			var step_contacts: Array[Dictionary] = contacts
			if not contacts.is_empty():
				step_contacts = _capsule_contacts(capsule, foot + Vector3.UP * 0.24)
				entry["raised_by_0_24m_contacts"] = _contact_names(step_contacts)
				entry["requires_small_step_clearance"] = step_contacts.is_empty()
			entry["pass"] = normal.y >= 0.65 and step_contacts.is_empty()
		clearances.append(entry)
		var check: Dictionary = entry.duplicate()
		check["name"] = "walking_capsule_clearance_%02d" % i
		tests.append(check)
	report["walking_clearances"] = clearances


func _capsule_contacts(capsule: CapsuleShape3D, foot: Vector3) -> Array[Dictionary]:
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.transform = Transform3D(Basis.IDENTITY, foot + Vector3.UP * 0.875)
	query.collision_mask = 1
	query.margin = 0.005
	query.collide_with_areas = false
	return get_world_3d().direct_space_state.intersect_shape(query, 16)


func _contact_names(contacts: Array[Dictionary]) -> Array:
	var result: Array = []
	for contact in contacts:
		var collider: Node = contact.collider as Node
		result.append(str(collider.get_parent().name) if is_instance_valid(collider) else "unknown")
	return result
