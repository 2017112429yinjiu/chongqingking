extends SceneTree
const WalkTest = preload("res://scripts/qa_delivery.gd")
var scene: Node3D
var game: Node3D
var lesson: Node3D
var bike: CharacterBody3D
var checks: Array = []
var output := ""
var crowd_tick := 0
var nearest_person := {"clearance_to_bike_m": INF}
var ever_failed := false
var joint_samples:Array=[]
var case_crossings:Array=[]
var sampled_case_frames:=0
var audit: Node
var injected_barrier: StaticBody3D

func _initialize() -> void: call_deferred("verify")

func check(label: String, passed: bool, details: Variant = "") -> bool:
	checks.append({"name":label,"pass":passed,"detail":details})
	print("DAY1 ",JSON.stringify(checks.back()))
	ever_failed = ever_failed or not passed
	return passed

func tap(key: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = key
	event.physical_keycode = key
	event.pressed = true
	root.push_input(event,true)
	var release := event.duplicate() as InputEventKey
	release.pressed = false
	root.push_input(release,true)

func frames(n: int) -> void:
	for i in range(n): await physics_frame

func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	if "--qa-still-frames" in OS.get_cmdline_user_args():
		RenderingServer.force_draw(false,1.0/60.0)
	else:
		await RenderingServer.frame_post_draw
	var pic := root.get_texture().get_image()
	check("frame_"+label,pic.save_png(output.path_join(label+".png")) == OK)

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
	check("last_mile_requires_walk",lesson.step == lesson.Step.LAST_METRES and not game.riding())
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
	check("handover_once",lesson.step == lesson.Step.DONE and game.earnings==8)
	tap(KEY_E)
	check("credit_and_regular_order_unlocked",game.delivered_count==1 and game.earnings==8 and game.shop.available(),game.ui())
	await frames(15)
	await capture("06_first_delivery")
	copy_checkpoint("completed")
	check("sampled_residents_clear_guide_bike",nearest_person.get("route","")!="" and nearest_person.clearance_to_bike_m>.25,nearest_person)
	check("two_bags_at_supported_hooks",lesson.demo.supports.size()==2 and lesson.demo.hooks.size()==2 and lesson.demo.parcel.global_position.distance_to(game.bag.global_position)>.32 and game.bag.visible and lesson.demo.parcel.visible)
	var d:Node3D=lesson.demo
	check("curled_fingers_at_crown",d.grasp_angle>35. and d.latest_grasp_error<.04,{"angle_degrees":d.grasp_angle,"distance_m":d.latest_grasp_error})
	check("three_distinct_wood_contacts",d.knock_distances.size()==3 and Array(d.knock_distances).all(func(x):return x<.025) and Array(d.knock_retractions).all(func(x):return x>.075),{"leaf":d.door.FACE_NAME,"surface":str(d.door.point),"gaps_m":Array(d.knock_distances),"withdrawals_m":Array(d.knock_retractions)})
	check("hung_at_supported_hook",d.latest_hook_error<.035,d.latest_hook_error)
	check_joints()
	check("both_guided_routes_arrived",audit.legs.size()==2 and audit.legs.values().all(func(leg):return leg.arrived))
	if "--test-roadblock" in OS.get_cmdline_user_args():
		check("temporary_barrier_detected_and_recovered",audit.issues.size()==1 and str(audit.issues[0].get("obstacle","")).contains("TestOnlyRoadblock") and audit.issues[0].get("end_reason","")=="forward_progress",audit.issues)
	else:
		check("no_blockage_jump_or_prolonged_airborne_contact",audit.issues.is_empty(),audit.issues)
	finish()

func sample_case(d:Node3D,stage:String) -> void:
	sampled_case_frames+=1
	var grip_box:Transform3D=d.mentor_box.box.global_transform.affine_inverse()*d.parcel.global_transform
	# Intersect actual bag slices with each side wall. Include the corner axes of the
	# rotated paper, so a projected bounding box alone cannot report a collision.
	const WALLS:=[Rect2(-.26,.35,.02,.46),Rect2(.24,.35,.02,.46),Rect2(-.241,.35,.482,.02),Rect2(-.241,.79,.482,.02)]
	for h:float in [.006,.035,.055,.09,.13,.18,.22,.254]:
		var p:Vector3=grip_box*Vector3(0,h,0)
		if p.y<.851 or p.y>1.209:continue
		var half_width:float=lerpf(.108,.123,clampf((h-.003)/.052,0.,1.)) if h<.055 else lerpf(.123,.116,clampf((h-.055)/.165,0.,1.))
		var half_depth:float=.068 if h<.035 else .079
		var outline:=PackedVector2Array()
		for s:Vector2 in [Vector2(-1,-1),Vector2(1,-1),Vector2(1,1),Vector2(-1,1)]:
			var v:=grip_box*Vector3(s.x*half_width,h,s.y*half_depth)
			outline.append(Vector2(v.x,v.z))
		for rect:Rect2 in WALLS:
			var end:=rect.end
			var polygon:=PackedVector2Array([rect.position,Vector2(end.x,rect.position.y),end,Vector2(rect.position.x,end.y)])
			if not Geometry2D.intersect_polygons(outline,polygon).is_empty():
				case_crossings.append({"stage":stage,"time":4.8-d.timer,"bag_center":str(p),"wall":str(rect)})
				return

func check_joints() -> void:
	var wrist:=0.
	var elbow_pair_high:=0
	var neck_clearance:=INF
	var tab_gap:=0.
	var step:=0.
	var previous:Dictionary={}
	var covered:Dictionary={}
	for row:Dictionary in joint_samples:
		var st:String=row.stage
		if st not in ["HANG","LOAD_BOX","UNLOAD"] or not row.has("R") or not row.has("L"):continue
		covered[st]=int(covered.get(st,0))+1
		if row.R.driven:wrist=maxf(wrist,row.R.wrist_deg)
		if st in ["LOAD_BOX","UNLOAD"]:
			if minf(row.R.elbow_above_shoulder_m,row.L.elbow_above_shoulder_m)>.01:elbow_pair_high+=1
			var t:=4.8-float(row.timer)
			if row.L.driven and (t>.37 and t<.91 or t>3.98 and t<4.52):tab_gap=maxf(tab_gap,row.L.reach_error_m)
			if row.R.driven and t>1.4 and t<3.21:
				neck_clearance=minf(neck_clearance,row.R.head_wrist_m)
				if previous.get("stage","")==st and int(row.frame)-int(previous.frame)<=5:
					var a:Array=previous.hand_xyz
					var b:Array=row.hand_xyz
					step=maxf(step,Vector3(a[0],a[1],a[2]).distance_to(Vector3(b[0],b[1],b[2]))/(row.frame-previous.frame))
				previous=row
	check("paper_clears_case_sides",sampled_case_frames>60 and case_crossings.is_empty(),{"sampled_frames":sampled_case_frames,"intersections":case_crossings.size(),"first":case_crossings.front() if not case_crossings.is_empty() else {}})
	check("working_arm_alignment",covered.size()==3 and wrist<25. and elbow_pair_high==0,{"samples":covered,"max_wrist_flex_deg":wrist,"both_elbows_above_shoulders":elbow_pair_high})
	check("box_hand_path",neck_clearance>.23 and tab_gap<.026 and step<.058,{"min_head_joint_to_wrist_m":neck_clearance,"max_lid_wrist_target_error_m":tab_gap,"peak_sampled_hand_travel_m_per_tick":step})

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
		var moving: bool=follow and Vector2(p.x-foot.x,p.z-foot.z).length()>2.45 and name_ in ["SHOP_EXIT","WALK_COUNTER","RETURN_BIKE","PUPIL_UNLOAD","LEAD_HOME","KNOCK","WALK_TO_HOOK","HANG","STEP_ASIDE","ORDER"]
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

func detail(d:Node3D,stage:String,label:="") -> void:
	var target:Vector3=d.walker.grip()
	var offset:Vector3=d.walker.global_basis*Vector3(-.70,.16,.45)
	if stage=="KNOCK":
		target=d.door.point
		offset=Vector3(.61,.16,.63)
	if stage in ["PICK_UP","LIFT_CLEAR"]:
		target=d.game.shopkeeper.food_end+Vector3.UP*.39
		offset=d.walker.global_basis*Vector3(-.79,.18,.47)
	if stage in ["HANG","RELEASE_HOOK"]:
		target=d.hooks[0]+Vector3(0,-.13,.06)
		offset=Vector3(.82,.26,.63)
	if stage in ["LOAD_BOX","UNLOAD"]:
		target=lesson.mentor.to_global(Vector3(.22,.98,.58))
		offset=lesson.mentor.global_basis*Vector3(1.45,.42,-2.10)
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.cull_mask&=~game.actor.FIRST_PERSON_BODY_LAYER
	camera.fov=40
	camera.global_position=target+offset
	camera.look_at(target)
	camera.make_current()
	camera.force_update_transform()
	await process_frame
	RenderingServer.camera_set_transform(camera.get_camera_rid(),camera.global_transform)
	await capture("detail_"+stage.to_lower() if label.is_empty() else label)
	game.actor.camera.make_current()
	camera.queue_free()

func walk(points: Array, label: String) -> bool:
	var row := await WalkTest._walk(scene,points,label)
	if not row["pass"]: await capture("blocked_"+label)
	return check(label,row["pass"],row)

func ride(label: String) -> bool:
	var mentor: CharacterBody3D = lesson.mentor
	var start := bike.global_position
	var recorded_ride := false
	var interrupted := false
	for frame in range(3200):
		if is_instance_valid(injected_barrier) and not injected_barrier.is_queued_for_deletion() and not audit.issues.is_empty():
			injected_barrier.queue_free()
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
			return check(label,parked and not game.riding() and start.distance_to(bike.global_position)>6.,{"student_end":str(bike.global_position),"mentor_end":str(mentor.global_position),"frames":frame})
		await physics_frame
	await capture("blocked_"+label)
	return check(label,false,{"bike":str(bike.global_position),"mentor":str(mentor.global_position),"waypoint":mentor.next_point,"wait":mentor.waiting,"arrived":mentor.arrived,"student_obstacle":bike.last_obstacle,"guide_obstacle":mentor.last_obstacle})

func sample_passing_distance() -> void:
	crowd_tick += 1
	if crowd_tick % 6 or not is_instance_valid(lesson.mentor) or not scene.street_block:return
	for track: Dictionary in scene.street_block.tracks:
		if track.car: continue
		var point: Vector3 = lesson.mentor.to_local(track.node.global_position)
		if absf(point.y) > .65: continue
		# Ground-plane clearance from the mentor scooter's .28 m capsule, excluding rider bodywork.
		var center_gap := Vector2(point.x,point.z-clampf(point.z,-.47,.47)).length()
		var edge_gap := center_gap-.28
		if edge_gap < nearest_person.clearance_to_bike_m:
			nearest_person = {"clearance_to_bike_m":edge_gap,"route":track.route,"stage":lesson.Step.keys()[lesson.step],"resident":str(track.node.global_position),"scooter":str(lesson.mentor.global_position)}

func copy_checkpoint(label: String) -> void:
	var saved := ConfigFile.new()
	var ok: bool = saved.load(lesson.record_path) == OK and int(saved.get_value("shift","step",-1)) == lesson.step
	if ok: ok = saved.save(output.path_join(label+".cfg")) == OK
	check("saved_"+label,ok)

func finish() -> void:
	FileAccess.open(output.path_join("joints.json"),FileAccess.WRITE).store_string(JSON.stringify(joint_samples))
	var hashes := {}
	for script in ["first_shift.tscn","scripts/main.gd","scripts/gameplay.gd","scripts/scooter_controller.gd","scripts/mentor_scooter.gd","scripts/day_one.gd","scripts/mentor_route_audit.gd","scripts/mentor_demonstration.gd","scripts/mentor_walker.gd","scripts/mentor_reach.gd","scripts/mentor_gaze.gd","scripts/mentor_arm.gd","scripts/scooter_visual.gd","scripts/kraft_paper.gdshader","scripts/mentor_hands.gd","scripts/teaching_door.gd","scripts/takeaway_bag.gd","scripts/shift_cargo_box.gd","assets/vehicles/first_shift_box.glb"]:
		hashes[script] = FileAccess.get_sha256("res://"+script)
	var f := FileAccess.open(output.path_join("first_shift.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"passed":not ever_failed,"engine":Engine.get_version_info().string,"display":DisplayServer.get_name(),"renderer":RenderingServer.get_current_rendering_method(),"source_sha256":hashes,"checks":checks,"demonstrations":lesson.demo.notes if lesson and lesson.demo else [],"mentor_route":audit.report() if audit else {},"nearest_walking_resident":nearest_person},"\t"))
	f.close()
	quit(2 if ever_failed else 0)
