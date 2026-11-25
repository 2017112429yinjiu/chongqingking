extends RefCounted
## One initial fixture placement only; thereafter actual walking and scooter physics.
static func run(main: Node3D) -> void:
	var actor: Node3D = main.explorer
	var game: Node3D = main.gameplay
	var tests: Array = []
	actor.begin_route_test(Vector3(-22.8,12.1,60.4),main._pickup)
	for frame in range(45): await main.get_tree().physics_frame
	tests.append(await _walk(main,[main._pickup+Vector3(.6,0,0)],"approach_shop"))
	tests.append({"name":"accept_order","pass":game.interact() and game.order==1})
	for frame in range(240): await main.get_tree().physics_frame
	tests.append({"name":"take_food","pass":game.interact() and game.order==3})
	tests.append(await _walk(main,[game.scooter.global_position+Vector3(-.7,0,1)],"walk_to_scooter"))
	tests.append({"name":"enter_scooter","pass":game.interact() and game.riding()})
	if game.riding():
		var scooter: CharacterBody3D = game.scooter
		scooter.automation=true
		scooter.test_throttle=1
		var start: Vector3 = scooter.global_position
		for frame in range(110): await main.get_tree().physics_frame
		scooter.test_throttle=0
		scooter.test_brake=true
		for frame in range(65): await main.get_tree().physics_frame
		tests.append({"name":"ride_from_real_shop_forecourt","pass":scooter.global_position.distance_to(start)>2 and scooter.is_on_floor(),"distance_m":scooter.global_position.distance_to(start),"last_obstacle":scooter.last_obstacle})
		tests.append({"name":"park_at_trip_endpoint","pass":scooter.park()})
		tests.append({"name":"exit_at_trip_endpoint","pass":game.interact() and not game.riding()})
		scooter.automation=false
	tests.append(await _walk(main,[Vector3(-20,12.8,52),Vector3(-20,15.6,30),Vector3(-18.5,17.2,19.7),Vector3(-49,16.5,19.7),Vector3(-51.2,16.4,19.5),Vector3(-54.9,16.44,19.5),game.Unit.LANDING,Vector3(-63.84,19.89,19.65)],"continuous_last_mile_to_house"))
	actor.camera.look_at(game.destination.global_position)
	actor._sync_angles()
	tests.append({"name":"resident_answers_at_201","pass":game.interact() and game.free_answered and game.order==3})
	tests.append(await _walk(main,[Vector3(-63.77,19.89,20.27)],"reach_resident_shelf"))
	actor.camera.look_at(game.destination.global_position)
	actor._sync_angles()
	game.interact()
	for frame in 90:await main.get_tree().physics_frame
	tests.append({"name":"deliver_at_residential_door","pass":game.order==4})
	game.interact()
	tests.append({"name":"single_delivery_credit","pass":game.delivered_count==1})
	actor.end_route_test()
	var passed: bool = true
	for test in tests: passed = passed and bool(test["pass"])
	var report: Dictionary = {"passed":passed,"initial_fixture_placements":1,"teleports_between_stages":0,"engine":Engine.get_version_info().string,"scene_sha256":FileAccess.get_sha256("res://assets/chongqing_district.glb"),"tests":tests}
	report["character_sha256"]=FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH)
	report["character_import_sha256"]=FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import")
	report["rider_sha256"]=FileAccess.get_sha256("res://assets/characters/rider_r18.glb")
	report["vehicle_sha256"]=FileAccess.get_sha256("res://assets/vehicles/scooter_r18.glb")
	report["controller_sha256"]=FileAccess.get_sha256("res://scripts/scooter_controller.gd")
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var output: String=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(output)
	FileAccess.open(output+"/delivery_end_to_end.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("CQ_DELIVERY_E2E ",JSON.stringify(report))
	main.get_tree().quit(0 if passed else 2)

static func _walk(main: Node3D, points: Array, name: String) -> Dictionary:
	var actor: Node3D = main.explorer
	var start: Vector3 = actor.body.global_position
	var previous: Vector3 = start
	var length: float = 0
	var max_frame: float = 0
	var reached: int = 0
	var stalled: Array = []
	actor.automation_driving=true
	actor.automation_axis=Vector2(0,-1)
	for point: Vector3 in points:
		actor.aim_route_test(point)
		for frame in range(1900):
			actor.aim_route_test(point)
			await main.get_tree().physics_frame
			var current: Vector3 = actor.body.global_position
			length+=Vector2(current.x-previous.x,current.z-previous.z).length()
			max_frame=maxf(max_frame,current.distance_to(previous))
			previous=current
			if Vector2(current.x-point.x,current.z-point.z).length()<.3:
				reached+=1
				break
			if frame==1899:
				for index in range(actor.body.get_slide_collision_count()):
					var collision: KinematicCollision3D=actor.body.get_slide_collision(index)
					var collider: Node3D=collision.get_collider()
					stalled.append({"mesh":str(collider.get_parent().name),"position":str(collision.get_position()),"normal":str(collision.get_normal())})
		if reached<points.find(point)+1:break
	actor.automation_axis=Vector2.ZERO
	for frame in range(20):await main.get_tree().physics_frame
	var result: Dictionary={"name":name,"pass":reached==points.size() and max_frame<1 and actor.body.is_on_floor(),"goals":points.size(),"reached":reached,"distance_m":length,"max_frame_displacement_m":max_frame,"end":str(actor.body.global_position),"stall_contacts":stalled}
	print("CQ_DELIVERY_STAGE ",JSON.stringify(result))
	return result
