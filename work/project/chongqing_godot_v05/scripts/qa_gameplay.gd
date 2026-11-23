extends RefCounted
## Tests use actual imported world collision. Teleportation only sets test fixtures.
static func run(main: Node3D) -> void:
	var actor: Node3D = main.explorer
	var game: Node3D = main.gameplay
	var tests: Array = []
	actor.set_mode(true)
	actor.can_control(false)
	actor.set_physics_process(false)
	actor.body.global_position = main._pickup + Vector3(0,0,10)
	tests.append({"name":"far_interaction_rejected","pass":not game.interact()})
	tests.append({"name":"delivery_requires_food","pass":not game.destination.available()})
	actor.body.global_position = main._pickup + Vector3(0,0,2)
	var sight_blocker: StaticBody3D = StaticBody3D.new()
	sight_blocker.collision_layer = 1
	var sight_collision: CollisionShape3D = CollisionShape3D.new()
	var sight_shape: BoxShape3D = BoxShape3D.new()
	sight_shape.size = Vector3(2,2,.2)
	sight_collision.shape = sight_shape
	sight_blocker.add_child(sight_collision)
	main.add_child(sight_blocker)
	sight_blocker.global_position = main._pickup + Vector3(0,1,1)
	await main.get_tree().physics_frame
	tests.append({"name":"wall_blocks_interaction","pass":not game.manager.reachable(game.shop)})
	sight_blocker.queue_free()
	await main.get_tree().physics_frame
	actor.body.global_position = main._pickup
	await main.get_tree().physics_frame
	tests.append({"name":"shop_accept_order","pass":game.interact() and game.order==1})
	game.interact()
	tests.append({"name":"cannot_take_unprepared_food","pass":game.order==1})
	for frame in range(240):
		await main.get_tree().physics_frame
	tests.append({"name":"food_ready","pass":game.order==2 and game.bag.visible})
	tests.append({"name":"food_pickup","pass":game.interact() and game.order==3 and not game.bag.visible})
	game.interact()
	tests.append({"name":"duplicate_pickup_rejected","pass":game.order==3})
	actor.set_walk_origin(Vector3(-63.84,19.94,19.65),game.destination.global_position)
	await main.get_tree().physics_frame
	tests.append({"name":"resident_answers_before_release","pass":game.interact() and game.order==3 and game.free_answered})
	actor.set_walk_origin(Vector3(-63.77,19.94,20.27),game.destination.global_position)
	await main.get_tree().physics_frame
	game.interact()
	for frame in 90:await main.get_tree().physics_frame
	tests.append({"name":"food_delivered","pass":game.order==4})
	game.interact()
	tests.append({"name":"delivery_idempotent","pass":game.delivered_count==1})
	var vehicle: CharacterBody3D = game.scooter
	tests.append({"name":"scooter_exists","pass":is_instance_valid(vehicle)})
	actor.body.global_position = vehicle.global_position+Vector3(1.4,0,0)
	await main.get_tree().physics_frame
	tests.append({"name":"approach_and_enter_scooter","pass":game.interact() and game.riding()})
	tests.append({"name":"unparked_exit_rejected","pass":not vehicle.exit_vehicle()})
	# Separate clear road fixture for repeatable motor tests.
	vehicle.global_position=Vector3(0,32.25,-78)
	vehicle.rotation=Vector3(0,-PI/2,0)
	vehicle.safe_park_position=vehicle.global_position
	vehicle.automation=true
	vehicle.test_throttle=1.0
	var start: Vector3 = vehicle.global_position
	var max_speed: float = 0
	for frame in range(150):
		await main.get_tree().physics_frame
		max_speed=maxf(max_speed,absf(vehicle.speed))
	tests.append({"name":"drive_actual_world","pass":vehicle.global_position.distance_to(start)>3 and vehicle.is_on_floor(),"distance_m":vehicle.global_position.distance_to(start),"last_obstacle":vehicle.last_obstacle,"end":str(vehicle.global_position)})
	tests.append({"name":"governed_speed","pass":max_speed<=6.01,"peak_mps":max_speed})
	var heading: float = vehicle.rotation.y
	vehicle.test_steer=.5
	for frame in range(20):
		await main.get_tree().physics_frame
	tests.append({"name":"steer_changes_heading","pass":absf(vehicle.rotation.y-heading)>.1})
	vehicle.test_steer=0
	vehicle.test_throttle=0
	vehicle.test_brake=true
	for frame in range(55):
		await main.get_tree().physics_frame
	tests.append({"name":"brake_stops","pass":absf(vehicle.speed)<.01})
	vehicle.test_brake=false
	vehicle.test_throttle=-1
	for frame in range(75):
		await main.get_tree().physics_frame
	tests.append({"name":"reverse","pass":vehicle.speed<-.5 and vehicle.speed>=-1.81,"speed":vehicle.speed})
	vehicle.test_throttle=0
	vehicle.test_brake=true
	for frame in range(30):
		await main.get_tree().physics_frame
	tests.append({"name":"park","pass":vehicle.park()})
	var obstruction: StaticBody3D = StaticBody3D.new()
	vehicle.set_physics_process(false)
	obstruction.collision_layer=1
	obstruction.collision_mask=0
	var collision: CollisionShape3D = CollisionShape3D.new()
	var shape: BoxShape3D = BoxShape3D.new()
	shape.size=Vector3(7,5,7)
	collision.shape=shape
	obstruction.add_child(collision)
	main.add_child(obstruction)
	obstruction.global_position=vehicle.global_position+Vector3.UP*1.5
	await main.get_tree().physics_frame
	tests.append({"name":"blocked_exit_rejected","pass":vehicle.find_exit()==null})
	obstruction.queue_free()
	await main.get_tree().physics_frame
	await main.get_tree().physics_frame
	vehicle.set_physics_process(true)
	var exited: bool=vehicle.exit_vehicle()
	await main.get_tree().physics_frame
	await main.get_tree().physics_frame
	tests.append({"name":"safe_exit_restores_walk","pass":exited and not game.riding() and actor.body.collision_mask==actor.walk_collision_mask and actor.is_physics_processing()})
	var bell_count: int = 0
	for target in game.manager.targets:
		if target.interaction_id.begins_with("doorbell."): bell_count+=1
	tests.append({"name":"thirteen_residential_doorbells_registered","pass":bell_count==13})
	actor.set_physics_process(false)
	actor.body.global_position=Vector3(-72.5,22.87,-28.88)
	await main.get_tree().physics_frame
	var selection: Node3D=game.manager.select()
	tests.append({"name":"worker_vestibule_bell_reachable","pass":selection!=null and str(selection.interaction_id).begins_with("doorbell.809889622")})
	actor.body.global_position=main._pickup
	await main.get_tree().physics_frame
	tests.append({"name":"return_to_shop_starts_next_order","pass":game.interact() and game.order==1 and game.delivered_count==1 and game.earnings==8})
	var all_ok: bool = true
	for test in tests:
		all_ok = all_ok and bool(test.pass)
	var report: Dictionary = {"revision":main.art_profile.get("art_revision",""),"engine":Engine.get_version_info().string,"passed":all_ok,"tests":tests,"scene_sha256":FileAccess.get_sha256("res://assets/chongqing_district.glb"),"character_sha256":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),"note":"Continuous physics drive on the imported upper road, followed by stationary interaction checks."}
	report["character_import_sha256"]=FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import")
	report["rider_sha256"]=FileAccess.get_sha256("res://assets/characters/rider_r18.glb")
	report["vehicle_sha256"]=FileAccess.get_sha256("res://assets/vehicles/scooter_r18.glb")
	report["controller_sha256"]=FileAccess.get_sha256("res://scripts/scooter_controller.gd")
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var output: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	var file: FileAccess = FileAccess.open(output+"/gameplay_test.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	print("R16_GAMEPLAY_QA ",JSON.stringify(report))
	main.get_tree().quit(0 if all_ok else 2)
