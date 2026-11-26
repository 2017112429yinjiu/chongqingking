extends "../map_review/survey.gd"

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for i in range(1600):
		if scene.gameplay:
			break
		await physics_frame
	assert(scene.gameplay != null)
	await frames(25)
	scene.hud.hide()
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.far = 145.0
	cam.make_current()

	var names := ["plot_01_street", "plot_02_street", "plot_37_street", "plot_42_room",
		"plot_56_room", "mapped_w704006729_1_inside", "mapped_w704006732_1_inside",
		"mapped_w704006733_1_inside", "mapped_w704006741_1_inside"]
	for id: int in [13, 14, 31, 63, 67, 71, 74]:
		names.append("plot_%02d_room" % id)
	var records: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_VIEWS")))
	for row: Dictionary in records.views:
		if row.key in names:
			await picture(row.key, row.title, vec(row.eye), vec(row.target), row.fov)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for p: Dictionary in layout.plots:
		if int(p.plot_id) != 37:
			continue
		var front: float = -p.depth * .5
		var foot := world(p, p.door_u, front - float(p.front_stair_m) - .55, 0)
		foot = public_floor([foot.x, -foot.z], p.height)
		var top := world(p, p.door_u, front - .7, 1.60)
		if foot.is_finite():
			await picture("plot_37_toe", "37 号梯脚进门", foot + Vector3.UP * 1.60, top)
			await picture("plot_37_back", "37 号门外回头", top, foot + Vector3.UP * 1.05)
	write_json("views.json", {"views": views, "renderer": RenderingServer.get_current_rendering_method()})
	quit(0)
