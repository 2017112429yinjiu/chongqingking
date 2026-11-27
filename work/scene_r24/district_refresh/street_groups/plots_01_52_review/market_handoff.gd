extends "../../continuous_site_walk.gd"

const Market := preload("res://scripts/outer_market_handoff.gd")

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory()
	graphics = DisplayServer.get_name() != "headless"
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	game = scene.gameplay
	var job = game.outer_market_handoff
	var actor = game.actor
	if not check("normal_game_has_market_handoff",job!=null and actor.walking and not game.lesson):
		quit(2)
		return
	var original: Vector3 = actor.body.global_position
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var plot: Dictionary = layout.plots.filter(func(row: Dictionary) -> bool: return int(row.plot_id)==1)[0]
	var return_origin := Market.counter_point(plot,-float(plot.width)*.27,-float(plot.depth)/2.-1.92,.075)
	check("scene_started_on_market_street_shoulder",original.distance_to(return_origin)<.27,enu(original))
	var stall := scene.find_child("OuterMarketSeller",true,false) as Node3D
	check("retained_produce_vendor_works_at_counter",stall!=null and stall.global_position.distance_to(job.sender.global_position)<2.1,
		enu(stall.global_position) if stall else [])
	var gate := Market.counter_point(plot,plot.door_u,-float(plot.depth)/2.-1.96,.06)
	var hall := Market.counter_point(plot,plot.door_u,-float(plot.depth)/2.+.94,.06)
	var aisle := Market.counter_point(plot,plot.door_u,-2.14,.05)
	var pickup := enu_point(job.stops[0].approach)
	var drop := enu_point(job.stops[1].approach)
	var route := [gate,hall,aisle,pickup]
	var middle := Market.counter_point(plot,-1.00,-1.35,.02)
	var walking_out := await leg_without_placement("01_street_to_working_stall",route)
	var turn: Vector3 = actor.body.global_position
	if walking_out.pass:
		var cash: int = game.earnings
		var completed: int = game.delivered_count
		actor.aim_route_test(job.sender.global_position)
		await frames(8)
		check("normal_prompt_selects_greens_seller",game.manager.select()==job.sender,enu(actor.body.global_position))
		tap(KEY_E)
		await frames(10)
		check("e_takes_parcel_from_seller",job.stage==job.Stage.CARRYING and game.public_handoff_in_progress())
		if graphics:
			await eye_frame("01-actual-vendor-pickup",enu(job.sender.global_position+Vector3.UP*.38))
		var cross := await leg_without_placement("01_carry_across_original_hall",[middle,drop])
		turn = actor.body.global_position
		if cross.pass:
			actor.aim_route_test(job.receiver.global_position)
			await frames(8)
			var ray := PhysicsRayQueryParameters3D.create(turn+Vector3.UP*1.3,job.receiver.global_position,1,[actor.body.get_rid()])
			var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
			check("normal_prompt_selects_dry_goods_counter",game.manager.select()==job.receiver,
				{"foot_enu":enu(turn),"target_enu":enu(job.receiver.global_position),
				 "line_of_sight_hit":"" if hit.is_empty() else String(hit.collider.get_parent().name)})
			tap(KEY_E)
			await frames(12)
			check("e_handoff_pays_once",job.stage==job.Stage.DELIVERED and game.earnings==cash+6
				and game.delivered_count==completed+1 and job.delivered_parcel.visible)
			tap(KEY_E)
			await frames(6)
			check("second_e_at_counter_does_not_pay",game.earnings==cash+6 and game.delivered_count==completed+1)
			if graphics:
				await eye_frame("01-actual-handoff",enu(job.receiver.global_position+Vector3.UP*.36))
			await leg_without_placement("01_reverse_same_aisle_to_street",[middle,pickup,aisle,hall,gate,original])
			check("return_to_same_market_street_shoulder",actor.body.global_position.distance_to(original)<.47,enu(actor.body.global_position))
	actor.end_route_test()
	FileAccess.open(output.path_join("market-handoff.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"start_enu":enu(original),"turn_enu":enu(turn),"checks":checks,"traces":walks,
		"teleports_between_legs":0,"controls":"normal E input through the scene viewport","renderer":RenderingServer.get_current_rendering_method(),
		"fold_scope":"Interior of the retained fictional public main hall"},"  "))
	quit(2 if ever_failed else 0)

func enu_point(row: Array) -> Vector3:
	return Vector3(row[0],row[2],-row[1])
