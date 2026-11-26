extends "../../riverside/survey.gd"
## Walk the registered 809889613 service route across the old 44 envelope.

const STATIONS := [[90.8,216.4], [92.99,211.57], [94.88,209.69],
	[98.09,208.0], [101.88,207.88], [109.0,210.89], [116.0,213.84]]

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var path: Array[Vector3] = []
	var sections := []
	for station: Array in STATIONS:
		path.append(ground_point(station, .042))
		sections.append({"east_north":station, "vertical_contacts":column(station)})
	await walk_pair("osm_way_809889613",path)
	var trace := {"scene":scene.scene_file_path,"source_way":809889613,
		"sections":sections,"checks":checks,"walks":walks}
	FileAccess.open(output.path_join("plot_44_way_809889613.json"),FileAccess.WRITE).store_string(JSON.stringify(trace,"  "))
	quit(2 if ever_failed else 0)
