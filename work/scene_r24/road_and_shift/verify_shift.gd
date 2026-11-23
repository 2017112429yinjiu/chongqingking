extends "../../scene_r24/day_one/verify.gd"
## Three-order regression on the real game entry, driving and interaction inputs.

func verify() -> void:
	output = preload("res://scripts/qa_context.gd").directory("res://verification_r24/first_shift")
	DirAccess.make_dir_recursive_absolute(output)
	if "--qa-still-frames" in OS.get_cmdline_user_args(): RenderingServer.render_loop_enabled = false
	scene = load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene = scene
	for tick in range(1800):
		if scene.get("gameplay") != null: break
		await physics_frame
	if not check("district_booted",scene.get("gameplay") != null):
		finish()
		return
	await frames(25)
	game = scene.gameplay
	lesson = game.lesson
	bike = game.scooter
	if not check("default_game_starts_at_registration",lesson != null and lesson.step == lesson.Step.CHECK_IN and game.actor.walking):
		finish()
		return
	lesson.record_path = output.path_join("test_checkpoint.cfg")
	physics_frame.connect(sample_passing_distance)
	audit = lesson.audit
	audit.issue_file = output.path_join("route_issues.json")
	await capture("01_arrival")
	check("early_order_and_bike_locked",not game.shop.available() and not lesson.can_mount() and not game.destination.available())
	tap(KEY_E)
	if not check("register_at_mentor",lesson.step == lesson.Step.MOUNT,game.actor.body.global_position):
		finish()
		return
	check("mentor_on_foot_at_check_in",not lesson.demo.walker.mounted and not lesson.can_mount())
	if not await attend("RIDING",false):
		finish()
		return
	if not await walk([bike.global_position+Vector3(-.4,0,-.95)],"walk_to_own_bike"):
		finish()
		return
	tap(KEY_E)
	if not check("mount_own_scooter",game.riding()):
		finish()
		return
	bike.automation = true
	await frames(440)
	var hold: Vector3 = lesson.mentor.global_position
	await frames(90)
	if not check("guide_waits_when_learner_stops",lesson.mentor.waiting and hold.distance_to(lesson.mentor.global_position)<.15 and hold.distance_to(lesson.STATION)>4.,hold):
		finish()
		return
	await capture("02_follow")
	if "--test-roadblock" in OS.get_cmdline_user_args():
		injected_barrier = StaticBody3D.new()
		injected_barrier.name = "TestOnlyRoadblock"
		var collision := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(4.5,1.4,.3)
		collision.shape = box
		injected_barrier.add_child(collision)
		scene.add_child(injected_barrier)
		injected_barrier.global_transform = lesson.mentor.global_transform
		injected_barrier.global_position += -lesson.mentor.global_basis.z*2.9+Vector3.UP*.65
	if not await ride("follow_to_noodle_shop"): 
		finish()
		return
	await frames(5)
	check("parked_at_shop",lesson.step == lesson.Step.SHOP)
	copy_checkpoint("shop")
	check("pupil_cannot_order_before_demo",not game.shop.available())
	if not await attend("PUPIL_PICKUP",true):
		finish()
		return
	check("mentor_took_separate_order",game.order==game.Order.AVAILABLE and lesson.demo.in_hand and lesson.demo.parcel.visible and game.earnings==0)
	await capture("peng_counter")
	if not await walk([Vector3(-26.7,12,56.7),scene._pickup+Vector3(.7,0,-.2)],"walk_to_counter"):
		finish()
		return
	tap(KEY_E)
	check("place_real_order",game.order == game.Order.PREPARING)
	await frames(270)
	game.actor.camera.look_at(game.bag.global_position+Vector3.UP*.12,Vector3.UP)
	game.actor._sync_angles()
	await frames(2)
	var bag_ray := PhysicsRayQueryParameters3D.create(game.actor.camera.global_position,game.bag.global_position+Vector3.UP*.12,1)
	var counter_hit: Dictionary = scene.get_world_3d().direct_space_state.intersect_ray(bag_ray)
	check("packed_meal_in_view_from_pickup",game.bag.visible and game.actor.camera.is_position_in_frustum(game.bag.global_position) and counter_hit.is_empty(),str(counter_hit))
	await capture("04_packed_meal")
	tap(KEY_E)
	check("take_packed_order",game.order == game.Order.CARRYING)
	await frames(3)
	check("cannot_deliver_before_second_leg",not game.destination.available())
	if not await attend("RIDING",true):
		finish()
		return
	copy_checkpoint("carrying")
	if not await walk([Vector3(-26.7,12,56.7),bike.last_exit],"return_to_parked_scooter"):
		finish()
		return
	tap(KEY_E)
	await frames(124)
	check("pupil_loads_separate_box",lesson.demo.student_stowed and not game.riding())
	tap(KEY_E)
	if not check("mount_with_order",game.riding(),game.ui()):
		finish()
		return
	bike.test_brake = false
	if not await ride("follow_to_courtyard_approach"):
		finish()
		return
	await frames(4)
	check("riders_park_at_real_address",lesson.step==lesson.Step.LAST_METRES and lesson.mentor.global_position.distance_to(parking_landmark())<9.0,lesson.mentor.global_position)
	copy_checkpoint("last_mile")
	if not await attend("PUPIL_UNLOAD",false):
		finish()
		return
	tap(KEY_E)
	await frames(124)
	check("pupil_retrieves_second_bag",lesson.demo.student_retrieved and lesson.demo.in_hand)
	if not await attend("PUPIL_DELIVERS",true):
		finish()
		return
	check("mentor_delivers_first",lesson.demo.door_shown and not lesson.demo.in_hand and game.order==game.Order.CARRYING and game.earnings==0)
	await capture("peng_delivered")
	if not await walk([lesson.demo.door.point+Vector3(.35,-1.35,-.10)],"walk_to_house_one"):
		finish()
		return
	game.actor.camera.look_at(lesson.demo.door.point,Vector3.UP)
	game.actor._sync_angles()
	tap(KEY_E)
	tap(KEY_E)
	check("rapid_input_cannot_skip_knock",not lesson.demo.student_knocked and game.earnings==0)
	await frames(46)
	await capture("pupil_knock")
	await frames(88)
	check("student_knocks_before_handover",lesson.demo.student_knocked and lesson.step==lesson.Step.LAST_METRES)
	check("pupil_knuckle_contacts_wood",lesson.demo.pupil_strikes.size()==3 and Array(lesson.demo.pupil_strikes).all(func(x):return x<.035),Array(lesson.demo.pupil_strikes))
	copy_checkpoint("knocked")
	if not await walk([lesson.demo.hooks[1]+Vector3(.05,-1.10,.40)],"reach_second_hook"):
		finish()
		return
	game.actor.camera.look_at(lesson.demo.hooks[1])
	game.actor._sync_angles()
	tap(KEY_E)
	check("credit_waits_for_release",game.earnings==0)
	await frames(136)
	check("order_one_credited_once",lesson.step==lesson.Step.RETURN and game.earnings==8 and game.delivered_count==1)
	copy_checkpoint("after_door")
	for index in [1,2]:
		if not await complete_extra(index):
			finish()
			return
	check("three_orders_paid_once",lesson.step==lesson.Step.DONE and game.earnings==24 and game.delivered_count==3 and game.shop.available(),game.ui())
	copy_checkpoint("completed")
	tap(KEY_E)
	check("repeat_interact_no_duplicate_credit",game.earnings==24)
	var at:Vector3=lesson.mentor.global_position
	var solo_frames:Dictionary={}
	for i in 15500:
		var d:Node3D=lesson.demo
		if DisplayServer.get_name()!="headless" and d.independent_job:
			var state:String=d.Action.keys()[d.action]
			if not solo_frames.has(state) and ((state=="PICK_UP" and d.timer<.18) or (state=="PUT_ON_SHELF" and d.timer<.24)):
				var cam:=Camera3D.new()
				scene.add_child(cam)
				cam.cull_mask&=~game.actor.FIRST_PERSON_BODY_LAYER
				cam.fov=48
				var look:Vector3=d.walker.global_position+Vector3.UP*1.02
				cam.global_position=look+Vector3(1.95,.60,1.85)
				cam.look_at(look)
				cam.make_current()
				cam.force_update_transform()
				await process_frame
				RenderingServer.camera_set_transform(cam.get_camera_rid(),cam.global_transform)
				await capture("independent_"+state.to_lower())
				game.actor.camera.make_current()
				cam.queue_free()
				solo_frames[state]=true
		if lesson.dispatch_deliveries>=1:break
		await physics_frame
	check("instructor_starts_own_next_job",lesson.mentor.global_position.distance_to(at)>9 and lesson.dispatch_deliveries>=1 and game.earnings==24,{"npc_deliveries":lesson.dispatch_deliveries,"trips":lesson.dispatch_leg,"position":str(lesson.mentor.global_position)})
	if "--test-roadblock" in OS.get_cmdline_user_args():
		check("barrier_detected_then_cleared",audit.issues.size()==1 and str(audit.issues[0].get("obstacle","")).contains("TestOnlyRoadblock") and audit.issues[0].get("end_reason","")=="forward_progress",audit.issues)
	else:check("empty_route_issue_log",audit.issues.is_empty(),audit.issues)
	await capture("after_shift")
	finish()

func parking_landmark()->Vector3:
	return lesson.Unit.COURT if "Unit" in lesson.get_script().get_script_constant_map() else lesson.demo.door.point

func pupil_return_path()->Array:
	if "Unit" in lesson.get_script().get_script_constant_map():return Array(lesson.Unit.downstairs(bike.last_exit))
	return [Vector3(-51.4,16.4,19.55),bike.last_exit]

func accessible_bike_side() -> Vector3:
	var direction:Vector3=(game.actor.body.global_position-bike.global_position).slide(Vector3.UP).normalized()
	return bike.global_position+direction*1.20

func complete_extra(index:int) -> bool:
	var d:Node3D=lesson.demo
	var title:="order_%d_" % (index+1)
	if index==1:
		if not await walk(pupil_return_path(),title+"back_to_vehicle"):return false
	else:
		if not await walk([bike.last_exit],title+"back_to_vehicle"):return false
	await frames(450)
	tap(KEY_E)
	if not check(title+"remount",game.riding() and lesson.step==lesson.Step.TO_SHOP,game.ui()):return false
	if not await ride(title+"back_to_shop"):return false
	if not await attend("PUPIL_PICKUP",true):return false
	if not await walk([Vector3(-26.7,12,56.7),scene._pickup+Vector3(.7,0,-.2)],title+"counter"):return false
	tap(KEY_E)
	await frames(270)
	tap(KEY_E)
	if index==1:
		if not check("spice_portion_required",game.order==game.Order.READY and game.condiments.state==game.condiments.State.ADDING):return false
		await frames(65)
		tap(KEY_E)
	if not check(title+"collected",game.order==game.Order.CARRYING,game.ui()):return false
	if not await attend("RIDING",true):return false
	if not await walk([Vector3(-26.7,12,56.7)],title+"leave_counter"):return false
	if not await walk([accessible_bike_side()],title+"load"):return false
	tap(KEY_E)
	await frames(126)
	tap(KEY_E)
	if not check(title+"mounted_with_own_parcel",game.riding() and d.student_stowed):return false
	if not await ride(title+"to_address"):return false
	if not await attend("PUPIL_UNLOAD",false):return false
	tap(KEY_E)
	await frames(125)
	if not await attend("PUPIL_SHELF",true):return false
	var shelf:Node3D=lesson.collection()
	var credits:int=game.earnings
	if index==2:
		check("unconfirmed_bays_locked",not shelf.bay_targets[0].available() and not shelf.bay_targets[1].available())
		if not await walk([shelf.to_global(Vector3(-.57,0,.56))],title+"call"):return false
		tap(KEY_E)
		if not check("customer_confirms_slot",lesson.recipient_answered,game.ui()):return false
	if not await walk([shelf.to_global(Vector3(-.34,0,.67))],title+"wrong_bay"):return false
	tap(KEY_E)
	if not check(title+"wrong_bay_rejected",game.order==game.Order.CARRYING and game.earnings==credits and lesson.chosen_slot==-1,game.toast):return false
	if not await walk([shelf.to_global(Vector3(.42,0,.64))],title+"correct_bay"):return false
	game.actor.camera.look_at(shelf.slots[1])
	game.actor._sync_angles()
	tap(KEY_E)
	if index==1:
		await frames(12)
		game.actor.camera.look_at(game.actor.camera.global_position+Vector3.BACK)
		game.actor._sync_angles()
		await frames(12)
		if not check("aborted_placement_keeps_order",d.action==d.Action.PUPIL_SHELF and game.order==game.Order.CARRYING and game.earnings==credits):return false
		game.actor.camera.look_at(shelf.slots[1])
		game.actor._sync_angles()
		tap(KEY_E)
	await frames(96)
	if not check(title+"both_real_bags_at_shelf",d.parcel.global_position.distance_to(shelf.slots[0])<.035 and game.bag.global_position.distance_to(shelf.slots[1])<.035 and game.earnings==credits+8,game.ui()):return false
	await capture(title+"delivered")
	return true

func attend(wanted: String, follow: bool) -> bool:
	var d: Node3D = lesson.demo
	var actor: Node3D = game.actor
	actor.automation_driving = true
	var trail: Array[Vector3] = []
	var prev := Vector3.INF
	var captured: Array[String] = []
	var paused_knock:=false
	for i in range(5600):
		var name_: String = d.Action.keys()[d.action]
		if name_ == wanted:
			actor.automation_axis=Vector2.ZERO
			return check("watched_"+wanted,true,{"walk_m":d.walker.travelled})
		if name_=="KNOCK" and not paused_knock and "--test-look-away" in OS.get_cmdline_user_args():
			paused_knock=true
			var before:float=d.timer
			actor.camera.look_at(actor.camera.global_position+Vector3.RIGHT)
			actor._sync_angles()
			await frames(90)
			check("demonstration_waits_for_line_of_sight",absf(before-d.timer)<.025 and d.knock_index==0)
		if name_ in ["LOAD_BOX","UNLOAD"] and d.in_hand:
			sample_case(d,name_)
		if i%3==0 and name_ in ["LOAD_BOX","UNLOAD","HANG","KNOCK","PICK_UP","LEAD_HOME"]:
			var row:Dictionary={"stage":name_,"timer":d.timer,"foot":str(d.walker.global_position),"frame":Engine.get_physics_frames(),"hand_xyz":Array([d.walker.grip().x,d.walker.grip().y,d.walker.grip().z])}
			for j in 2:
				var key:="L" if j else "R"
				if key in d.walker.joints_world:
					row[key]=d.walker.joints_world[key].duplicate()
			joint_samples.append(row)
		var p:Vector3 = d.walker.global_position
		if prev.distance_to(p)>.32:
			trail.append(p)
			prev=p
		var foot:Vector3=actor.body.global_position
		while trail.size()>1 and Vector2(foot.x-trail[0].x,foot.z-trail[0].z).length()<.55: trail.pop_front()
		var moving: bool=follow and Vector2(p.x-foot.x,p.z-foot.z).length()>2.45 and name_ in ["SHOP_EXIT","WALK_COUNTER","RETURN_BIKE","PUPIL_UNLOAD","LEAD_HOME","KNOCK","WALK_TO_HOOK","HANG","STEP_ASIDE","ORDER","TO_SHELF","PUT_ON_SHELF","CLEAR_SHELF"]
		if moving and not trail.is_empty():
			actor.aim_route_test(trail[0])
			actor.automation_axis=Vector2(0,-1)
		else:
			actor.automation_axis=Vector2.ZERO
			var focus:Vector3 = p+Vector3.UP*1.12
			if name_ in ["PACK","PICK_UP"]: focus=d.game.shopkeeper.food_end+Vector3.UP*.3
			if name_ in ["LOAD_BOX","UNLOAD"]: focus=lesson.mentor.to_global(Vector3(0,1.15,.53))
			if name_=="KNOCK":focus=d.door.point
			if name_=="HANG":focus=d.hooks[0]
			actor.camera.look_at(focus)
			actor._sync_angles()
		if name_ not in captured and (name_=="LOAD_BOX" and d.timer<2.53 or name_=="UNLOAD" and d.timer<2.30 or name_=="PICK_UP" and d.timer<.12 or name_=="HANG" and d.timer<.40 or name_=="LEAD_HOME" and p.x < -28. or name_=="KNOCK" and d.timer<.92):
			await capture("peng_"+name_.to_lower())
			captured.append(name_)
			if name_ in ["PICK_UP","LEAD_HOME","KNOCK","HANG","LOAD_BOX","UNLOAD"] and DisplayServer.get_name()!="headless":
				await detail(d,name_)
		if "--contact-motion" in OS.get_cmdline_user_args() and DisplayServer.get_name()!="headless" and i%4==0:
			var stage:="pickup" if name_ in ["PICK_UP","LIFT_CLEAR"] else ("knock" if name_=="KNOCK" else "")
			if name_=="LEAD_HOME" and p.x < -29. and p.x > -31.:stage="carry"
			if name_ in ["LOAD_BOX","UNLOAD","HANG","RELEASE_HOOK"]:stage="hang" if name_=="RELEASE_HOOK" else name_.to_lower()
			if stage!="":await detail(d,name_,"reel_%s_%08d"%[stage,Engine.get_physics_frames()])
		await physics_frame
	actor.automation_axis=Vector2.ZERO
	await capture("failed_"+wanted)
	return check("watched_"+wanted,false,{"action":d.Action.keys()[d.action],"walker":str(d.walker.global_position),"student":str(actor.body.global_position),"waypoint":d.walker.index,"sight":d.waiting_for_view,"timer":d.timer,"hold":d.walking_wait,"blocked":d.walker.blocked_s,"packing":game.shopkeeper.packing,"released":game.shopkeeper.released})

func ride(label: String) -> bool:
	var mentor: CharacterBody3D = lesson.mentor
	var start := bike.global_position
	var travelled:=0.
	var previous:Vector3=start
	var filmed_court_lane:=false
	var recorded_ride := false
	var interrupted := false
	for frame in range(4400):
		travelled+=bike.global_position.distance_to(previous)
		previous=bike.global_position
		if is_instance_valid(injected_barrier) and not injected_barrier.is_queued_for_deletion() and not audit.issues.is_empty():
			injected_barrier.queue_free()
		if not filmed_court_lane and lesson.step==lesson.Step.TO_YARD and bike.global_position.y>15.7 and bike.global_position.x< -35 and absf(bike.global_position.z-19.7)<2.2:
			filmed_court_lane=true
			await capture("court_from_saddle")
		if not recorded_ride and bike.speed > 1.3 and mentor.speed > 1.1 and bike.global_position.distance_to(start)>4.:
			recorded_ride = true
			await capture("03_both_riding" if lesson.step == lesson.Step.TO_SHOP else "05_riding_uphill")
		if "--test-dismount" in OS.get_cmdline_user_args() and not interrupted and recorded_ride and lesson.step == lesson.Step.TO_SHOP:
			interrupted = true
			bike.test_brake = true
			bike.test_throttle = 0.
			await frames(60)
			if not check("mid_route_park_and_dismount",bike.park() and game.interact() and not game.riding()):
				return false
			await frames(60)
			var stopped_at := mentor.global_position
			await frames(120)
			check("mentor_waits_for_dismounted_learner",mentor.waiting and stopped_at.distance_to(mentor.global_position)<.06 and lesson.step==lesson.Step.TO_SHOP)
			if not check("remount_after_practice_stop",game.interact() and game.riding()):return false
		var to: Vector3 = mentor.global_position - bike.global_position
		to.y = 0
		var distance := to.length()
		var steer := (-bike.global_basis.z).signed_angle_to(to.normalized(),Vector3.UP)
		bike.test_steer = clampf(steer*2.1,-1.,1.)
		var speed_limit := clampf((distance-2.4)*.95,.0,3.8)
		bike.test_throttle = float(bike.speed < speed_limit and distance>2.8)
		bike.test_brake = bike.speed > speed_limit+.4 or distance < 2.7
		if mentor.arrived and distance < 5.4:
			bike.test_throttle = 0.
			bike.test_brake = true
		if mentor.arrived and distance < 5.6 and absf(bike.speed) < .04:
			tap(KEY_P)
			var parked: bool = bike.parked
			tap(KEY_E)
			return check(label,parked and not game.riding() and travelled>6. and mentor.global_position.distance_to(mentor.path[-1])<1.6,{"wheel_travel_m":travelled,"student_end":str(bike.global_position),"mentor_end":str(mentor.global_position),"frames":frame})
		await physics_frame
	await capture("blocked_"+label)
	return check(label,false,{"bike":str(bike.global_position),"mentor":str(mentor.global_position),"waypoint":mentor.next_point,"wait":mentor.waiting,"arrived":mentor.arrived,"student_obstacle":bike.last_obstacle,"guide_obstacle":mentor.last_obstacle})

func finish() -> void:
	FileAccess.open(output.path_join("joints.json"),FileAccess.WRITE).store_string(JSON.stringify(joint_samples))
	var hashes := {}
	for script in ["first_shift.tscn","scripts/main.gd","scripts/gameplay.gd","scripts/scooter_controller.gd","scripts/mentor_scooter.gd","scripts/shift_collection_shelf.gd","scripts/district_connections_r24.gd","shaders/street_repairs_r24.gdshaderinc","assets/courtyard_grade/grade.glb","assets/courtyard_grade/footwear.png","scripts/day_one.gd","scripts/mentor_route_audit.gd","scripts/mentor_demonstration.gd","scripts/mentor_walker.gd","scripts/mentor_reach.gd","scripts/mentor_gaze.gd","scripts/mentor_arm.gd","scripts/scooter_visual.gd","scripts/kraft_paper.gdshader","scripts/mentor_hands.gd","scripts/teaching_door.gd","scripts/takeaway_bag.gd","scripts/shift_cargo_box.gd","assets/vehicles/first_shift_box.glb"]:
		hashes[script] = FileAccess.get_sha256("res://"+script)
	var f := FileAccess.open(output.path_join("first_shift.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"passed":not ever_failed,"engine":Engine.get_version_info().string,"display":DisplayServer.get_name(),"renderer":RenderingServer.get_current_rendering_method(),"source_sha256":hashes,"checks":checks,"demonstrations":lesson.demo.notes if lesson and lesson.demo else [],"mentor_route":audit.report() if audit else {},"nearest_walking_resident":nearest_person},"\t"))
	f.close()
	quit(2 if ever_failed else 0)
