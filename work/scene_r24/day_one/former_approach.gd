extends SceneTree
## Reproduce the retired east-to-west line beside the stone flight on the unchanged block.
func _initialize() -> void: call_deferred("run_probe")

func run_probe() -> void:
	var main: Node3D = load("res://first_shift.tscn").instantiate()
	root.add_child(main)
	current_scene = main
	while not main.gameplay: await physics_frame
	var game: Node3D = main.gameplay
	var lesson: Node3D = game.lesson
	var bike: CharacterBody3D = game.scooter
	var guide: CharacterBody3D = lesson.mentor
	var output := "res://verification_r24/first_shift/former_approach"
	DirAccess.make_dir_recursive_absolute(output)
	lesson.audit.issue_file = output+"/route_issues.json"
	lesson._place_vehicle(guide,Vector3(9,11.9,58),PI/2)
	lesson._place_vehicle(bike,Vector3(13.5,11.9,58),PI/2)
	lesson._walk_from(Vector3(10.8,11.9,57.1),guide.global_position+Vector3.UP)
	for i in range(20): await physics_frame
	game.interact()
	await preload("res://scripts/qa_delivery.gd")._walk(main,[bike.global_position+Vector3(-.4,0,-.95)],"former_start")
	game.interact()
	bike.automation = true
	for tick in range(2): await physics_frame
	guide.guide_to(PackedVector3Array([Vector3(-5,11.8,58),Vector3(-22.6,11.6,57.8)]))
	for tick in range(2400):
		if tick > 528:
			var delta: Vector3 = guide.global_position-bike.global_position
			delta.y = 0
			var steer := (-bike.global_basis.z).signed_angle_to(delta.normalized(),Vector3.UP)
			var limit := clampf((delta.length()-2.4)*.95,0.,3.8)
			bike.test_steer = clampf(steer*2.1,-1.,1.)
			bike.test_throttle = float(bike.speed<limit and delta.length()>2.8)
			bike.test_brake = bike.speed>limit+.4 or delta.length()<2.7
		await physics_frame
		if not lesson.audit.issues.is_empty() or guide.arrived: break
	var result: Dictionary = lesson.audit.report()
	result["reproduced"] = not lesson.audit.issues.is_empty()
	result["scooter"] = str(guide.global_position)
	result["last_contact"] = guide.last_obstacle
	FileAccess.open(output+"/diagnosis.json",FileAccess.WRITE).store_string(JSON.stringify(result,"\t"))
	print("FORMER_APPROACH ",JSON.stringify(result))
	quit(0 if result.reproduced else 2)
