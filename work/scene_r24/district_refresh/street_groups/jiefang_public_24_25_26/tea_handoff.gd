extends "../../continuous_site_walk.gd"

func point(enu_point:Array)->Vector3:
	return Vector3(enu_point[0],enu_point[2],-enu_point[1])

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	graphics=DisplayServer.get_name()!="headless"
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	var game=scene.gameplay
	var tea=game.riverside_tea
	if not check("standard_game_tea_job",tea!=null):
		quit(2)
		return
	var actor=game.actor
	var area: Dictionary=scene.get_node("City/OuterDistrict500").get_meta("riverside_tea")
	var start: Vector3=actor.body.global_position
	check("normal_play_at_new_land_side",actor.walking and start.distance_to(point(area.approach))<.16,enu(start))
	var vendor: Node3D=scene.find_child("RiversideTeaWorker",true,false)
	check("tea_vendor_at_new_stand",vendor!=null and vendor.global_position.distance_to(point(area.stand_east_north_up))<.07)
	var pickup:=point(tea.stops[0].approach)
	var drop:=point(tea.stops[1].approach)
	var out:=await leg_without_placement("street_to_tea_vendor",[pickup])
	if out.pass:
		actor.aim_route_test(tea.sender.global_position)
		await frames(9)
		var stock_money:int=game.earnings
		var stock_count:int=game.delivered_count
		check("pickup_on_foot_from_vendor",game.manager.select()==tea.sender and game.interact() and tea.stage==tea.Stage.CARRYING,enu(actor.body.global_position))
		check("normal_jobs_block_second_pickup_during_handoff",game.public_handoff_in_progress() and not game.shop.available())
		if graphics:
			scene.hud.hide()
			await eye_frame("tea-player-pickup",null)
		var mid:Vector3=pickup.lerp(drop,.47)
		var trip:=await leg_without_placement("carry_tea_along_land_side",[mid,drop])
		if trip.pass:
			actor.aim_route_test(tea.receiver.global_position)
			await frames(9)
			check("actual_shelf_handoff_and_credit",game.manager.select()==tea.receiver and game.interact() and tea.stage==tea.Stage.DELIVERED and game.earnings==stock_money+6 and game.delivered_count==stock_count+1)
			check("no_double_credit",not game.interact() and game.earnings==stock_money+6)
			if graphics:await eye_frame("tea-player-handoff",null)
			var return_trip:=await leg_without_placement("tea_shelf_back_to_same_place",[mid,pickup,start])
			check("return_same_walkside",return_trip.pass and actor.body.global_position.distance_to(start)<.48,enu(actor.body.global_position))
	actor.end_route_test()
	FileAccess.open(output.path_join("tea-handoff.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"traces":walks,"tea_stage":tea.stage,"renderer":RenderingServer.get_current_rendering_method()},"  "))
	quit(2 if ever_failed else 0)
