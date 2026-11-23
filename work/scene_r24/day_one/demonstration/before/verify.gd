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
	copy_checkpoint("carrying")
	if not await walk([Vector3(-26.7,12,56.7),bike.last_exit],"return_to_parked_scooter"):
		finish()
		return
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
	if not await walk([Vector3(-24.5,14,40),Vector3(-20,14,40),Vector3(-20,15.6,30),Vector3(-18.5,17.2,19.7),Vector3(-49,16.5,19.7),Vector3(-51.2,16.4,19.5),scene._dropoff+Vector3(1.15,0,0)],"walk_to_house_one"):
		finish()
		return
	game.actor.camera.look_at(game.destination.global_position + Vector3.UP*.18,Vector3.UP)
	game.actor._sync_angles()
	tap(KEY_E)
	check("handover_once",lesson.step == lesson.Step.DONE and game.earnings==8)
	tap(KEY_E)
	check("credit_and_regular_order_unlocked",game.delivered_count==1 and game.earnings==8 and game.shop.available(),game.ui())
	await frames(15)
	await capture("06_first_delivery")
	copy_checkpoint("completed")
	check("sampled_residents_clear_guide_bike",nearest_person.get("route","")!="" and nearest_person.clearance_to_bike_m>.25,nearest_person)
	check("both_guided_routes_arrived",audit.legs.size()==2 and audit.legs.values().all(func(leg):return leg.arrived))
	if "--test-roadblock" in OS.get_cmdline_user_args():
		check("temporary_barrier_detected_and_recovered",audit.issues.size()==1 and str(audit.issues[0].get("obstacle","")).contains("TestOnlyRoadblock") and audit.issues[0].get("end_reason","")=="forward_progress",audit.issues)
	else:
		check("no_blockage_jump_or_prolonged_airborne_contact",audit.issues.is_empty(),audit.issues)
	finish()

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
	var hashes := {}
	for script in ["first_shift.tscn","scripts/main.gd","scripts/gameplay.gd","scripts/scooter_controller.gd","scripts/mentor_scooter.gd","scripts/day_one.gd","scripts/mentor_route_audit.gd"]:
		hashes[script] = FileAccess.get_sha256("res://"+script)
	var f := FileAccess.open(output.path_join("first_shift.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"passed":not ever_failed,"engine":Engine.get_version_info().string,"display":DisplayServer.get_name(),"renderer":RenderingServer.get_current_rendering_method(),"source_sha256":hashes,"checks":checks,"mentor_route":audit.report() if audit else {},"nearest_walking_resident":nearest_person},"\t"))
	f.close()
	quit(2 if ever_failed else 0)
