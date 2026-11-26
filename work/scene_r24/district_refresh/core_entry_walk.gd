extends "riverside/survey.gd"
## Record both directions across each registered core-to-expansion joint.

const ENTRY_PLAN := "res://../../scene_r24/district_refresh/evidence/core-entry-stations.json"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ENTRY_PLAN))
	var measured := {}
	for key: String in plan:
		var path: Array[Vector3] = []
		var hits := []
		for stop: Array in plan[key].walk_points:
			var floor := public_floor(stop, float(plan[key].floor_y))
			path.append(floor)
			hits.append({"station":stop,"point":str(floor)})
		measured[key]=hits
		if path.has(Vector3.INF):
			check(key+"_supported_path",false,hits)
			continue
		await walk_pair(key,path)
	FileAccess.open(output.path_join("core-entry-walk.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"engine":Engine.get_version_info().string,"scene":scene.scene_file_path,
		"candidate":scene.scene_identity.district_500,
		"parked_scooter_xyz":str(scene.gameplay.scooter.global_position),
		"entries":measured,"walks":walks,"checks":checks},"  "))
	quit(2 if ever_failed else 0)
