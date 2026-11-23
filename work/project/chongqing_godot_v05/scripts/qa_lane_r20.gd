extends RefCounted

static func check(tests: Array, label: String, result: bool) -> void:
	tests.append({"name":label, "pass":result})

static func run(main: Node3D) -> void:
	var tests := []
	var game: Node3D = main.gameplay
	var actor: Node3D = main.explorer
	var lane: Node3D = main.get_node("City/UpperLaneR20")
	var board: Node3D
	for target: Node3D in game.manager.targets:
		if target.interaction_id == "residents.notice.upper":
			board = target
	check(tests, "notice_registered", is_instance_valid(board))
	var world := main.get_world_3d().direct_space_state
	var outward := Vector3(.869,0,.493)
	var tangent := Vector3(.493,0,-.87)
	var origin := Vector3(-39.5608,0,-40.9019)
	var anchors_hit := 0
	for s: float in [1.55,3.7,5.95,8.2,10.45,12.7,15.3]:
		var center := origin + tangent*s + Vector3.UP*(25.96+.149*s)
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(center+outward*.35,center,1))
		if not hit.is_empty() and str(hit.collider.get_parent().name).begins_with("COL_R20_Returned_handrail"):
			anchors_hit += 1
	check(tests, "seven_handhold_physics_samples", anchors_hit==7)
	var cap: MeshInstance3D = lane.find_child("R20_Hand_laid_treads_slab", true, false)
	check(tests, "weathered_treads_imported", is_instance_valid(cap))
	if board != null:
		actor.set_mode(true)
		var near: Vector3 = board.global_position + outward*.90
		var ground := world.intersect_ray(PhysicsRayQueryParameters3D.create(near+Vector3.UP,near-Vector3.UP*3.,1))
		if not ground.is_empty():
			actor.body.global_position = ground.position + Vector3.UP*.06
		await main.get_tree().physics_frame
		check(tests, "approach_and_select_board", game.manager.select()==board)
		for page: String in game.RESIDENT_NOTICES:
			check(tests, "read_"+page.substr(0,3), game.interact() and game.toast==page)
			for letter in page:
				if letter.unicode_at(0)>127 and not main.UI_FONT.has_char(letter.unicode_at(0)):
					check(tests, "missing_UI_glyph_"+letter, false)
		check(tests, "reading_preserves_order", game.order==0 and game.earnings==0)
		check(tests, "cycles_to_first_notice", game.interact() and game.toast==game.RESIDENT_NOTICES[0])
		actor.body.global_position = board.global_position-outward*.38-Vector3.UP
		check(tests, "wall_blocks_notice", not game.manager.reachable(board))
		actor.body.global_position = board.global_position + tangent*4.
		check(tests, "cannot_read_from_far", not game.manager.reachable(board))
	if is_instance_valid(game.rinse_tap):
		var tap: Node3D=game.rinse_tap
		var stand := tap.global_position + Vector3(-.7,0.,-.45)
		var floor_hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(stand+Vector3.UP,stand-Vector3.UP*2.,1))
		actor.body.global_position = floor_hit.position + Vector3.UP*.06
		await main.get_tree().physics_frame
		check(tests,"operate_tap_in_world",game.interact() and tap.stream_mesh.visible and tap.splash.emitting and tap.sound.playing)
		check(tests,"close_tap_in_world",game.interact() and not tap.stream_mesh.visible and not tap.sound.playing)
		game.interact()
		for frame in range(310): await main.get_tree().physics_frame
		check(tests,"water_shuts_off_after_five_seconds",tap.remaining==0. and not tap.splash.emitting and not tap.sound.playing)
	else:
		check(tests,"tap_present",false)
	var seats: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/lane_r20/tree_seats.json"))
	for place: Dictionary in seats.places:
		var front := Vector3(place.front[0],place.front[1],place.front[2])
		var seat := Vector3(place.seat[0],place.seat[1],place.seat[2])
		var seat_outward := Vector3(front.x-seat.x,0.,front.z-seat.z).normalized()
		actor.body.global_position=front+seat_outward*.44+Vector3.UP*.11
		await main.get_tree().physics_frame
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(seat+Vector3.UP*.35,seat-Vector3.UP*.13,1))
		check(tests,"collidable_seat_"+str(place.arc),not hit.is_empty() and str(hit.collider.get_parent().name).begins_with("COLH_R20_Tree_seat") and absf(hit.position.y-seat.y)<.01)
		check(tests,"sit_from_street_"+str(place.arc),game.interact() and actor.seated)
		var foot_before: Vector3=actor.body.global_position
		for frame in range(65):await main.get_tree().physics_frame
		check(tests,"seated_eye_"+str(place.arc),actor.camera.global_position.distance_to(seat+Vector3.UP*.83)<.005)
		check(tests,"stand_and_keep_footing_"+str(place.arc),game.interact() and not actor.seated and foot_before.distance_to(actor.body.global_position)<.02 and actor.walking)
	check(tests,"rest_preserves_order", game.order==0 and game.earnings==0)
	var flags:=lane.find_child("R20_Court_paving_step_concrete",true,false) as MeshInstance3D
	var sane_colors:=false
	if flags:
		var colors: PackedColorArray=flags.mesh.surface_get_arrays(0)[Mesh.ARRAY_COLOR]
		sane_colors=not colors.is_empty()
		for tint in colors:
			sane_colors=sane_colors and tint.r>=tint.g-.012 and tint.g>=tint.b-.012 and tint.r>.32
	check(tests,"neutral_imported_court_stone_colors",sane_colors)
	var garden:=lane.find_child("COL_R20_Terrace_soil_soil_dark",true,false)
	check(tests,"raised_soil_has_physical_top",garden!=null and garden.has_node("CQ_StaticCollision"))
	if main.art_profile.get("court_resident",false):
		await preload("res://scripts/qa_court_resident.gd").run(main,tests)
	var lod_root: Node3D=main.get_node_or_null("City/SpatialMeterDetails")
	check(tests,"112_matching_meter_ranges",lod_root!=null and lod_root.find_children("MeterClose_*","MeshInstance3D",true,false).size()==112 and lod_root.find_children("MeterFar_*","MeshInstance3D",true,false).size()==112)
	if lod_root:
		var aligned:=true
		for far_meter: MeshInstance3D in lod_root.find_children("MeterFar_*","MeshInstance3D",true,false):
			var close:=lod_root.find_child(str(far_meter.name).replace("MeterFar_","MeterClose_"),true,false) as MeshInstance3D
			aligned=aligned and close!=null and close.custom_aabb==far_meter.custom_aabb and close.transform.is_equal_approx(far_meter.transform) and close.visibility_range_end==far_meter.visibility_range_begin
		check(tests,"near_and_far_geometry_share_distance_boundary",aligned)
	var passed := true
	for t: Dictionary in tests:
		passed = passed and t["pass"]
	var report := {"passed":passed,"tests":tests,"hit_samples":anchors_hit}
	var context := preload("res://scripts/qa_context.gd")
	context.decorate(report,main)
	var dir: String=context.directory("res://verification_r20/current")
	DirAccess.make_dir_recursive_absolute(dir)
	FileAccess.open(dir+"/lane_test.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	main.get_tree().quit(0 if passed else 2)
