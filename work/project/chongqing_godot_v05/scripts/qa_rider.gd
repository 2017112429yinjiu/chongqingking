extends RefCounted
## Actual world driving plus measured skeletal contacts and unaltered GPU captures.
static func run(main: Node3D) -> void:
	var tree: SceneTree=main.get_tree()
	var vehicle: CharacterBody3D=main.gameplay.scooter
	var art: Node3D=vehicle.articulation
	var actor: Node3D=main.explorer
	var tests: Array=[]
	var captures: Array=[]
	var output: String="res://verification_r18/rider_current"
	if DisplayServer.get_name()=="headless":output="res://verification_r18/rider_physics"
	output=preload("res://scripts/qa_context.gd").directory(output)
	DirAccess.make_dir_recursive_absolute(output)
	actor.set_mode(true);actor.set_physics_process(false);actor.can_control(false)
	tests.append({"name":"unoccupied_scooter_hides_rider","pass":not art.human.visible})
	vehicle.global_position=Vector3(0,32.25,-78);vehicle.rotation=Vector3(0,-PI/2,0);vehicle.safe_park_position=vehicle.global_position
	vehicle.automation=true
	for i in range(30):await tree.physics_frame
	tests.append({"name":"enter_shows_rider","pass":vehicle.enter(actor) and art.human.visible})
	for i in range(45):await tree.physics_frame
	tests.append({"name":"stationary_left_foot_support","pass":art.support_amount>.99})
	vehicle.set_physics_process(false)
	art._pose("ride_support",.5)
	await tree.process_frame
	var skeleton: Skeleton3D=art.human.find_children("*","Skeleton3D",true,false)[0]
	var ankle: int=skeleton.find_bone("Bip01 L Foot")
	if ankle<0:ankle=skeleton.find_bone("Bip01_L_Foot")
	var ankle_world: Vector3=skeleton.global_transform*skeleton.get_bone_global_pose(ankle).origin
	var arc_expected: Vector3=art.global_transform*Vector3(-.361875,.437125,-.015)
	tests.append({"name":"imported_foot_arc_clears_deck_midpoint","pass":ankle_world.distance_to(arc_expected)<.003,"ankle_target_error_m":ankle_world.distance_to(arc_expected)})
	art._pose("ride_support",0.0)
	vehicle.set_physics_process(true)
	captures.append(await _capture(main,output,"mounted_stop",Vector3(2.5,1.5,-2.5)))
	var start: Vector3=vehicle.global_position
	var initial_roll: float=art.roll_phase
	vehicle.test_throttle=1
	for i in range(120):await tree.physics_frame
	tests.append({"name":"wheels_roll_during_actual_drive","pass":vehicle.global_position.distance_to(start)>2 and absf(angle_difference(initial_roll,art.roll_phase))>.05,"distance":vehicle.global_position.distance_to(start)})
	tests.append({"name":"feet_on_deck_at_speed","pass":art.support_amount<.01})
	tests.append(_contacts(art,"straight_grip_contacts"))
	tests.append(_tyres(art,"rolling_tyre_ground_contact"))
	captures.append(await _capture(main,output,"riding_side",Vector3(3.0,1.4,0)))
	vehicle.test_steer=.75
	for i in range(24):await tree.physics_frame
	tests.append({"name":"front_wheel_and_handlebar_steer","pass":absf(art.steering.rotation.y)>.15 and absf(art.front_wheel.get_parent().rotation.y)>.15})
	tests.append(_contacts(art,"turn_grip_contacts"))
	tests.append(_tyres(art,"steered_tyre_ground_contact"))
	captures.append(await _capture(main,output,"riding_turn",Vector3(1.8,1.6,-2.4)))
	vehicle.test_steer=0;vehicle.test_throttle=0;vehicle.test_brake=true
	for i in range(110):await tree.physics_frame
	tests.append({"name":"braked_rider_returns_support","pass":absf(vehicle.speed)<.01 and art.support_amount>.99})
	var stopped_roll: float=art.roll_phase
	for i in range(15):await tree.physics_frame
	tests.append({"name":"stopped_wheels_do_not_spin","pass":absf(angle_difference(stopped_roll,art.roll_phase))<.001})
	vehicle.test_brake=false;vehicle.test_throttle=-1
	for i in range(65):await tree.physics_frame
	tests.append({"name":"reverse_rider_keeps_deck_pose","pass":vehicle.speed<-.5 and art.support_amount<.01})
	tests.append(_contacts(art,"reverse_grip_contacts"))
	vehicle.test_throttle=0;vehicle.test_brake=true
	for i in range(90):await tree.physics_frame
	tests.append({"name":"park_with_rider","pass":vehicle.park()})
	captures.append(await _capture(main,output,"parked_support",Vector3(-2.6,1.2,-1.7)))
	var before_exit: Vector3=vehicle.global_position
	var exit_ok: bool=vehicle.exit_vehicle()
	tests.append({"name":"exit_hides_rider","pass":exit_ok and not art.human.visible})
	actor.set_physics_process(false)
	var exit_trace: Array=[]
	for i in range(30):
		await tree.physics_frame
		if i<4:
			var collisions: Array=[]
			for j in range(vehicle.get_slide_collision_count()):
				var hit: KinematicCollision3D=vehicle.get_slide_collision(j)
				collisions.append({"collider":str(hit.get_collider().get_path()),"normal":str(hit.get_normal())})
			exit_trace.append({"position":str(vehicle.global_position),"actor":str(actor.body.global_position),"collisions":collisions})
	tests.append({"name":"parked_vehicle_stays_after_exit","pass":vehicle.global_position.distance_to(before_exit)<.02,"displacement":vehicle.global_position.distance_to(before_exit),"trace":exit_trace})
	tests.append({"name":"exit_restores_actor_collision","pass":actor.body.collision_mask==actor.walk_collision_mask and actor.body.collision_layer==2})
	tests.append({"name":"parked_stand_extended","pass":absf(art.stand.rotation.z)<.001})
	captures.append(await _capture(main,output,"exited_parked",Vector3(2.4,1.5,2.4)))
	var passed: bool=true
	for test: Dictionary in tests:passed=passed and bool(test.pass)
	var report: Dictionary={"passed":passed,"tests":tests,"captures":captures,"scope":"One initial road fixture, actual physics thereafter; captures freeze vehicle physics briefly. No mount/dismount body animation, crowd or full-body continuous collision acceptance.","engine":Engine.get_version_info().string}
	for pair: Array in [["rider","res://assets/characters/rider_r18.glb"],["rider_import","res://assets/characters/rider_r18.glb.import"],["vehicle","res://assets/vehicles/scooter_r18.glb"],["controller","res://scripts/scooter_controller.gd"],["visual","res://scripts/scooter_visual.gd"]]:
		report[pair[0]+"_sha256"]=FileAccess.get_sha256(pair[1])
	preload("res://scripts/qa_context.gd").decorate(report,main)
	FileAccess.open(output+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("R18_RIDER_QA ",JSON.stringify(report));tree.quit(0 if passed else 2)

static func _contacts(art: Node3D,label: String) -> Dictionary:
	var skeleton: Skeleton3D=art.human.find_children("*","Skeleton3D",true,false)[0]
	var distances: Array=[]
	var pivot: Vector3=Vector3(0,1.10,-.40)
	var turn: Basis=Basis(Vector3.UP,art.steer_angle)
	for side in ["L","R"]:
		var sign: float=-1.0 if side=="L" else 1.0
		var bone: int=skeleton.find_bone("Bip01 "+side+" Hand")
		if bone<0:bone=skeleton.find_bone("Bip01_"+side+"_Hand")
		if bone<0:return {"name":label,"pass":false,"reason":"hand bone missing"}
		var actual: Vector3=skeleton.global_transform*skeleton.get_bone_global_pose(bone).origin
		var expected: Vector3=art.global_transform*(pivot+turn*Vector3(sign*.315,.049,.097))
		distances.append(actual.distance_to(expected))
	return {"name":label,"pass":distances.max()<.002,"wrist_target_errors_m":distances}

static func _tyres(art: Node3D,label: String) -> Dictionary:
	var gaps: Array=[]
	for wheel: Node3D in [art.rear_wheel,art.front_wheel]:
		var points: Array[Vector3]=[]
		for mesh: MeshInstance3D in wheel.find_children("*","MeshInstance3D",true,false):
			if not "rubber" in str(mesh.name):continue
			for surface in range(mesh.mesh.get_surface_count()):
				for vertex: Vector3 in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(mesh.global_transform*vertex)
		points.sort_custom(func(a: Vector3,b: Vector3) -> bool:return a.y<b.y)
		var gap: float=INF
		for point in points.slice(0,8):
			var ray: PhysicsRayQueryParameters3D=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.20,point-Vector3.UP*.20,1)
			var hit: Dictionary=art.get_world_3d().direct_space_state.intersect_ray(ray)
			if not hit.is_empty():gap=minf(gap,point.y-hit.position.y)
		gaps.append(gap)
	return {"name":label,"pass":absf(gaps[0])<.018 and absf(gaps[1])<.018,"rear_front_min_clearance_m":gaps,"sample":"eight lowest imported rubber vertices per wheel"}

static func _capture(main: Node3D,output: String,label: String,offset: Vector3) -> Dictionary:
	if DisplayServer.get_name()=="headless":return {"name":label,"image":"not captured in headless physics run"}
	var vehicle: Node3D=main.gameplay.scooter
	vehicle.set_physics_process(false)
	var camera: Camera3D=main.explorer.camera
	var old_fov: float=camera.fov
	camera.fov=50.0
	main.hud.visible=false
	camera.global_position=vehicle.global_transform*offset
	camera.look_at(vehicle.global_position+Vector3.UP*.92)
	for i in range(12):await main.get_tree().process_frame
	await RenderingServer.frame_post_draw
	main.get_viewport().get_texture().get_image().save_png(output+"/"+label+".png")
	var result: Dictionary={"name":label,"vehicle_position":str(vehicle.global_position),"speed":vehicle.speed,"steer":vehicle.articulation.steer_angle,"support":vehicle.articulation.support_amount,"camera":str(camera.global_position)}
	vehicle.set_physics_process(true)
	camera.fov=old_fov;main.hud.visible=true
	return result
