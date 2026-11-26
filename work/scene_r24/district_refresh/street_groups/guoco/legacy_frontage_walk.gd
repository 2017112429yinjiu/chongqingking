extends "../../riverside/survey.gd"
## Re-run both old low-street traces without bypassing their recorded obstacles.

const ORIGINAL := [[132.,-99.],[145.,-100.],[161.,-100.],[175.,-98.],
	[191.,-96.],[204.,-96.],[216.,-94.]]
const REVISED_START := [[138.,-99.4],[145.,-100.],[161.,-100.],[175.,-98.],
	[191.,-96.],[204.,-96.],[216.,-94.]]

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var profiles := {}
	for label: String in ["original_low_street","later_low_street_start"]:
		var stations: Array = ORIGINAL if label == "original_low_street" else REVISED_START
		var route: Array[Vector3] = []
		var profile := []
		for station: Array in stations:
			var floor := ground_point(station,.04)
			route.append(floor)
			profile.append({"station":station,"contacts":column(station)})
		profiles[label] = profile
		await walk_pair(label,route)
	FileAccess.open(output.path_join("legacy_frontage_walk.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"candidate":scene.scene_identity.district_500,
		"checks":checks,"walks":walks,"profiles":profiles},"  "))
	quit(2 if ever_failed else 0)
