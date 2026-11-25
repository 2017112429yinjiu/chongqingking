extends "../../scene_r24/day_one/verify.gd"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	scene = load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene = scene
	for i in 1800:
		if scene.get("gameplay"):
			break
		await physics_frame
	await frames(25)
	game = scene.gameplay
	if not check("direct_entry_bike", game != null and game.lesson == null and game.scooter.global_position.x > 100.0):
		quit(2)
		return
	var start: Vector3 = game.actor.body.global_position
	check("player_facing_own_bike", start.distance_to(game.scooter.global_position)<2.3, str(start))
	tap(KEY_E)
	await frames(4)
	check("normal_interaction_mounts", game.riding(), game.ui().prompt)
	if game.riding():
		bike = game.scooter
		bike.automation = true
		var parked_at: Vector3 = bike.global_position
		bike.test_throttle = 1
		await frames(85)
		bike.test_throttle = 0
		bike.test_brake = true
		await frames(120)
		check("ride_from_shortcut", parked_at.distance_to(bike.global_position)>1.0, parked_at.distance_to(bike.global_position))
		tap(KEY_P)
		await frames(3)
		tap(KEY_E)
		await frames(20)
		check("park_and_dismount",not game.riding() and game.actor.walking, str(game.actor.body.global_position))
	FileAccess.open(output.path_join("explore.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
