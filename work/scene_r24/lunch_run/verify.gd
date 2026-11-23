extends "../../scene_r24/day_one/verify.gd"
const Unit=preload("res://scripts/unit_interior.gd")
const UPHILL=[Vector3(-25.1,12,57.1),Vector3(-25.3,12,55.25),Vector3(-24.7,12.3,52),Vector3(-25.3,12.7,48),Vector3(-24.6,14,40.5),Vector3(-25.9,14.7,35),Vector3(-25.8,15.5,29),Vector3(-25.3,16,21.6)]
var lunch:Node3D
var cfg_path:String
var second_route:=false
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	var args:=OS.get_cmdline_user_args()
	cfg_path=output.path_join("lunch.cfg")
	for arg in args:
		if arg.begins_with("--restart="):
			await restart(arg.trim_prefix("--restart="))
			end_run()
			return
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene=scene
	for tick in 1500:
		if scene.gameplay:break
		await physics_frame
	await frames(25)
	game=scene.gameplay
	lesson=game.lesson
	lunch=game.lunch
	if not check("practice_at_real_counter",lunch!=null and lunch.can_offer() and lesson.record_path.is_empty() and game.earnings==24):end_run();return
	lesson.record_path=cfg_path
	second_route="--homes-first" in args
	tap(KEY_G)
	check("manifest_before_accept",lunch.preview and not lunch.active and not FileAccess.file_exists(cfg_path))
	await frames(13)
	await capture("01_offer")
	tap(KEY_G)
	check("declining_has_no_charge",not lunch.preview and not lunch.active and game.earnings==24)
	tap(KEY_G)
	tap(KEY_E)
	if not check("batch_accepted",lunch.active and lunch.hand_count()==0 and game.earnings==24):end_run();return
	tap(KEY_TAB)
	check("paid_trip_uses_walking_and_riding",game.actor.walking and not game.actor.review_shortcuts)
	tap(KEY_V)
	tap(KEY_E)
	check("kitchen_not_ready",lunch.hand_count()==0)
	if second_route:
		await frames(1340)
		check("all_three_supported_at_counter",lunch.parcels.all(func(parcel):return parcel.visible) and lunch.counters[2].y+.50<lunch.counters[0].y)
		game.actor.camera.look_at(lunch.counters[1]+Vector3.UP*.13)
		game.actor._sync_angles()
		await frames(10)
		await capture("all_three_orders")
		var label:Label3D=lunch.parcels[1].ticket
		var detail_camera:=Camera3D.new()
		scene.add_child(detail_camera)
		detail_camera.global_position=label.global_position+label.global_basis.z*.43+Vector3.UP*.025
		detail_camera.look_at(label.global_position)
		detail_camera.make_current()
		await frames(5)
		await capture("paper_ticket")
		game.actor.camera.make_current()
		detail_camera.queue_free()
	else:
		await frames(333)
	tap(KEY_E)
	if not check("first_pickup_201",lunch.states[1]==lunch.State.HELD):end_run();return
	select_ticket(0 if not second_route else 2)
	await frames(12 if second_route else 1040)
	tap(KEY_E)
	select_ticket(2 if not second_route else 0)
	tap(KEY_E)
	check("third_bag_stays_on_counter",lunch.hand_count()==2 and lunch.states[lunch.selected]==lunch.State.COUNTER)
	await frames(20)
	await capture("02_counter_full")
	var left_id:int=lunch.left_ticket
	var right_id:int=lunch.right_hand()
	var selected_before:int=lunch.selected
	tap(KEY_V)
	await frames(3)
	check("reading_tickets_keeps_each_bag_in_its_hand",lunch.right_hand()==right_id and lunch.left_ticket==left_id and right_id!=left_id and "%03d"%lunch.ticket_number(right_id) in game.bag.ticket.text)
	select_ticket(selected_before)
	if "--scooter" in args:
		await ride_with_bags()
		end_run()
		return
	if second_route:
		select_ticket(2)
		if not await to_hall():end_run();return
		if not await deliver_flat(2):end_run();return
		if not await deliver_flat(1):end_run();return
		if not await return_shop(true):end_run();return
		tap(KEY_E)
		if not await court(true):end_run();return
	else:
		select_ticket(0)
		if not await court(true):end_run();return
		if not await return_shop(false):end_run();return
		select_ticket(2)
		tap(KEY_E)
		if not check("collect_remaining_bag",lunch.hand_count()==2):end_run();return
		if not await to_hall():end_run();return
		if not await walk([Vector3(-63.87,19.89,19.65)],"wrong_door_with_202"):end_run();return
		await face_press(Unit.DOOR_POINTS[0])
		check("wrong_door_does_not_answer_or_pay",not lunch.answered[1] and game.earnings==33 and "小票" in game.toast)
		select_ticket(1)
		if not await deliver_flat(1):end_run();return
		var saved:=ConfigFile.new()
		saved.load(cfg_path)
		DirAccess.copy_absolute(cfg_path,output.path_join("two_paid.cfg"))
		check("save_contains_distinct_receipts",saved.get_value("lunch","states")==[2,2,1] and saved.get_value("shift","deliveries")==5)
		if not await deliver_flat(2):end_run();return
		tap(KEY_E)
	var record:=ConfigFile.new()
	record.load(cfg_path)
	check("all_receipts_settle_once",not lunch.active and game.delivered_count==6 and game.earnings==24+lunch.awards[0]+lunch.awards[1]+lunch.awards[2] and record.get_value("shift","earnings")==game.earnings,{"awards":lunch.awards,"elapsed":lunch.elapsed,"earnings":game.earnings})
	check("time_changes_actual_fee",lunch.awards[0]==(6 if second_route else 9))
	await frames(15)
	await capture("05_receipt")
	end_run()

func select_ticket(i:int)->void:
	for n in 3:
		if lunch.selected==i:return
		tap(KEY_V)

func face_press(p:Vector3)->void:
	game.actor.camera.look_at(p)
	game.actor._sync_angles()
	await frames(4)
	tap(KEY_E)
	await frames(2)

func to_hall()->bool:
	return await walk(UPHILL+[Vector3(-48.5,16.4,19.65),Unit.COURT,Vector3(-54.9,16.44,19.5),Unit.LANDING],"shop_to_second_floor")

func return_shop(from_hall:bool)->bool:
	var path:Array=[]
	if from_hall:path=[Unit.LANDING,Vector3(-54.9,16.44,19.5),Unit.COURT,Vector3(-48.5,16.4,19.65)]
	else:path=[Vector3(-37.6,16.6,20.5)]
	var lane:=UPHILL.duplicate()
	lane.reverse()
	return await walk(path+lane+[scene._pickup+Vector3(.7,0,-.2)],"back_to_kitchen")

func court(from_shop:bool)->bool:
	var rack:Node3D=lunch.rack
	var lane:Array=UPHILL.duplicate() if from_shop else []
	if not await walk(lane+[rack.to_global(Vector3(-.58,0,1.05)),rack.to_global(Vector3(-.58,0,.63))],"reach_court_button"):return false
	select_ticket(0)
	await face_press(rack.call_point)
	if not check("court_recipient_confirms",lunch.answered[0],{"pos":game.actor.body.global_position,"prompt":game.ui().prompt}):return false
	if not await walk([rack.to_global(Vector3(.38,0,.57))],"try_bay_B"):return false
	await face_press(rack.slots[1]+Vector3.UP*.1)
	check("bay_B_refuses_A",lunch.states[0]==lunch.State.HELD and game.shelf_time<0. and "甲位" in game.toast)
	if not await walk([rack.to_global(Vector3(-.39,0,.55))],"reach_bay_A"):return false
	await face_press(rack.slots[0]+Vector3.UP*.12)
	await frames(89)
	await capture("03_court_rack")
	return check("court_parcel_released",lunch.states[0]==lunch.State.PAID and lunch.parcels[0].global_position.distance_to(rack.slots[0])<.01,{"p":game.actor.body.global_position,"prompt":game.ui().prompt,"t":lunch.elapsed})

func deliver_flat(i:int)->bool:
	select_ticket(i)
	var hallway:=Vector3(-62.14,19.89,19.1)
	var path:=[hallway,Vector3(-62.16,19.89,13.65),Vector3(-62.56,19.89,13.65)] if i==2 else [hallway,Vector3(-63.87,19.89,19.65)]
	if not await walk(path,"knock_%d"%i):return false
	await face_press(Unit.DOOR_POINTS[i-1])
	if not check("resident_answers_%d"%i,lunch.answered[i],game.ui().prompt):return false
	var foot:=Vector3(-63.77,19.89,20.27) if i==1 else Vector3(-62.55,19.89,14.55)
	if not await walk([foot],"access_shelf_%d"%i):return false
	var earnings:int=game.earnings
	await face_press(Unit.SHELVES[i-1]+Vector3.UP*.12)
	tap(KEY_V)
	tap(KEY_E)
	check("release_owns_ticket_%d"%i,lunch.selected==i and game.earnings==earnings and game.shelf_time>=0.)
	await frames(35)
	var hand:="left" if lunch.left_ticket==i else "right"
	var hand_ik:SkeletonIK3D=lesson.demo.pupil_ik if hand=="left" else lesson.demo.pupil_hang_ik
	check("placing_with_"+hand,hand_ik.is_running() and hand_ik.influence>.90)
	await capture("04_%d_%s_hand"%[200+i,hand])
	await frames(65)
	return check("paid_%d"%i,lunch.states[i]==lunch.State.PAID and lunch.parcels[i].global_position.distance_to(Unit.SHELVES[i-1])<.01,{"time":lunch.elapsed,"fee":lunch.awards[i]})

func restart(source:String)->void:
	if DirAccess.copy_absolute(source,cfg_path)!=OK:check("source_file",false);return
	# Rebuild the world and lesson against a real checkpoint instead of injecting ticket fields.
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=preload("res://scripts/day_one.gd").new()
	game.add_child(lesson)
	game.lesson=lesson
	lesson.setup(game,cfg_path)
	lunch=game.lunch
	await frames(25)
	if "--finished" in OS.get_cmdline_user_args():
		check("paid_slip_restored",not lunch.active and not lunch.recap.is_empty() and lunch.states==[2,2,2] and game.earnings==56)
		if not await walk([Vector3(-24.7,12.3,52),Vector3(-25.3,12,55.25),Vector3(-25.1,12,57.1),scene._pickup+Vector3(.7,0,-.2)],"return_from_saved_bike"):return
		tap(KEY_G)
		check("repeat_offer_optional",lunch.preview and game.earnings==56)
		tap(KEY_G)
		tap(KEY_E)
		check("single_after_batch",game.order==game.Order.PREPARING and "014" in game.bag.ticket.text and not lunch.active and lunch.recap.is_empty())
		return
	if not check("resume_two_paid_one_held",lunch.active and lunch.states==[2,2,1] and game.delivered_count==5 and game.earnings==45):return
	if not await deliver_flat(2):return
	check("reopen_does_not_pay_again",game.earnings==56 and game.delivered_count==6 and not lunch.active)

func ride_with_bags()->void:
	bike=game.scooter
	if not await walk([Vector3(-25.1,12,57.1),Vector3(-25.3,12,55.25),Vector3(-24.35,12.3,52.4),bike.global_position+Vector3(.87,0,.1)],"approach_own_scooter_with_two"):return
	tap(KEY_E)
	await frames(8)
	if not check("both_meals_board",game.riding() and lunch.hand_count()==2):return
	var inner:Node3D=game.lesson.demo.pupil_box.box
	var positions:Array=[]
	for i in 3:
		if lunch.states[i]==lunch.State.HELD:
			positions.append(inner.to_local(lunch.parcels[i].global_position))
	if not check("two_closed_lid_slots",positions.size()==2 and absf(positions[0].z-positions[1].z)>.19 and not game.bag.visible,positions):return
	bike.automation=true
	bike.test_throttle=1.
	var start:Vector3=bike.global_position
	var top:=0.
	var hits:Dictionary={}
	var goal:=Vector3(-25.7,16,26)
	for frame in 900:
		var heading:Vector3=(goal-bike.global_position).slide(Vector3.UP)
		bike.test_steer=clampf((-bike.global_basis.z).signed_angle_to(heading.normalized(),Vector3.UP)*2.2,-1.,1.)
		bike.test_throttle=float(bike.speed<3.9)
		await physics_frame
		top=maxf(top,bike.speed)
		for hit_index in bike.get_slide_collision_count():
			var hit:KinematicCollision3D=bike.get_slide_collision(hit_index)
			hits[str(hit.get_collider().get_path())]=str(hit.get_normal())
		if bike.global_position.z<goal.z+.6:break
	bike.test_throttle=0.
	bike.test_brake=true
	await frames(85)
	check("ridden_distance",bike.global_position.distance_to(start)>22. and bike.global_position.y-start.y>2.0 and top>1.,{"metres":bike.global_position.distance_to(start),"top_m_s":top,"start":str(start),"end":str(bike.global_position),"hits":hits,"obstacle":bike.last_obstacle})
	tap(KEY_P)
	tap(KEY_E)
	await frames(15)
	check("both_meals_leave_with_rider",not game.riding() and lunch.hand_count()==2 and game.bag.visible and game.earnings==24)
	await capture("both_meals_after_parking")
	if await walk([Vector3(-25.3,16,21.6)],"park_to_court_lane"):
		await court(false)

func end_run()->void:
	FileAccess.open(output.path_join("trip.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"\t"))
	quit(2 if ever_failed else 0)
