extends RefCounted
## Uncut Movie Maker take of actual motor, steer, support and exit states.
static func run(main: Node3D) -> void:
	var tag: String="r18_rider08"
	var camera_side: float=1.0
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--motion-tag="):tag=argument.trim_prefix("--motion-tag=")
		if argument=="--left-side":camera_side=-1.0
	assert(tag.is_valid_identifier())
	var evidence: Dictionary={"capture_start_unix":Time.get_unix_time_from_system(),"scripted_inputs":true,"initial_fixture_placements":1,"camera_side":camera_side,"scripts":{},"events":[],"source":"actual Godot physics and native rendered frames"}
	for pair: Array in [["rider","res://assets/characters/rider_r18.glb"],["rider_import","res://assets/characters/rider_r18.glb.import"],["vehicle","res://assets/vehicles/scooter_r18.glb"]]:evidence[pair[0]+"_sha256"]=FileAccess.get_sha256(pair[1])
	for script: String in ["scooter_controller","scooter_visual","gameplay","qa_rider_motion"]:evidence.scripts[script]=FileAccess.get_sha256("res://scripts/"+script+".gd")
	var vehicle: Node3D=main.gameplay.scooter
	var actor: Node3D=main.explorer
	main.hud.visible=false;actor.set_mode(true);actor.set_physics_process(false);actor.can_control(false)
	vehicle.global_position=Vector3(0,32.25,-78);vehicle.rotation=Vector3(0,-PI/2,0);vehicle.safe_park_position=vehicle.global_position;vehicle.automation=true
	actor.camera.fov=48
	for frame in range(420):
		if frame==20:evidence.events.append({"frame":frame,"enter":vehicle.enter(actor)})
		if frame==60:vehicle.test_throttle=1
		if frame==132:vehicle.test_steer=.60
		if frame==150:vehicle.test_steer=0;vehicle.test_throttle=0;vehicle.test_brake=true
		if frame==240:vehicle.test_brake=false;vehicle.test_throttle=-1
		if frame==270:vehicle.test_throttle=0;vehicle.test_brake=true
		if frame==300:evidence.events.append({"frame":frame,"park":vehicle.park()})
		if frame==360:
			evidence.events.append({"frame":frame,"exit":vehicle.exit_vehicle()});actor.set_physics_process(false)
		var angle: float=deg_to_rad(65.0+float(frame)/420.0*85.0)
		actor.camera.global_position=vehicle.global_position+Vector3(cos(angle)*3.4,1.8,camera_side*sin(angle)*3.4)
		actor.camera.look_at(vehicle.global_position+Vector3.UP*.95)
		if frame%30==0:evidence.events.append({"frame":frame,"position":str(vehicle.global_position),"speed":vehicle.speed,"support":vehicle.articulation.support_amount,"steering":vehicle.articulation.steer_angle})
		await main.get_tree().process_frame
	DirAccess.make_dir_recursive_absolute("res://verification_r18/motion_takes")
	FileAccess.open("res://verification_r18/motion_takes/"+tag+".json",FileAccess.WRITE).store_string(JSON.stringify(evidence,"\t"))
	print("R18_RIDER_MOTION_COMPLETE");main.get_tree().quit()
