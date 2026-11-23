extends SceneTree
const Shift = preload("res://scripts/day_one.gd")
var tests: Array = []

func _initialize() -> void: call_deferred("verify")

func verify() -> void:
	var folder: String = preload("res://scripts/qa_context.gd").directory("res://verification_r24/first_shift/native02")
	for label: String in ["shop","carrying","last_mile","knocked","completed"]:
		var scene = load("res://main.tscn").instantiate()
		root.add_child(scene)
		current_scene = scene
		while not scene.gameplay: await physics_frame
		var game: Node3D = scene.gameplay
		var shift: Node3D = Shift.new()
		game.lesson = shift
		game.add_child(shift)
		shift.setup(game,folder.path_join(label+".cfg"))
		for tick in range(30): await physics_frame
		var ok: bool = game.actor.walking and game.actor.body.is_on_floor() and not game.riding()
		match label:
			"shop": ok = ok and shift.step==Shift.Step.SHOP and not game.shop.available() and not shift.demo.shop_shown
			"carrying": ok = ok and shift.step==Shift.Step.TO_YARD and game.order==game.Order.CARRYING and not game.destination.available() and not shift.mentor.path.is_empty()
			"last_mile": ok = ok and shift.step==Shift.Step.LAST_METRES and game.order==game.Order.CARRYING and not game.destination.available() and not shift.demo.door_shown
			"knocked": ok = ok and shift.step==Shift.Step.LAST_METRES and shift.demo.student_knocked and shift.demo.door_shown and game.destination.available() and game.earnings==0 and game.destination.global_position.distance_to(shift.demo.hooks[1])<.02
			"completed": ok = ok and shift.step==Shift.Step.DONE and game.earnings==8 and game.delivered_count==1 and game.shop.available() and not is_instance_valid(shift.mentor)
		tests.append({"checkpoint":label,"passed":ok,"objective":game.ui().objective,"feet":str(game.actor.body.global_position)})
		print("DAY1_RESUME ",JSON.stringify(tests.back()))
		scene.queue_free()
		await process_frame
		await process_frame
	var passed := tests.all(func(row):return row.passed)
	FileAccess.open(folder.path_join("resume.json"),FileAccess.WRITE).store_string(JSON.stringify({"passed":passed,"checkpoints":tests},"\t"))
	quit(0 if passed else 2)
