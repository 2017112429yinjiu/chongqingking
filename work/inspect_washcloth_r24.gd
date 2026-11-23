extends SceneTree

const QA = preload("res://scripts/qa_context.gd")
const EYE := Vector3(-47.675976, 22.049192, -6.868392)
const TARGET := Vector3(-49., 21.959192, -10.)

func _initialize() -> void:
	call_deferred("run")

func capture_to(view: Viewport, path: String) -> bool:
	for frame in 12:
		await RenderingServer.frame_post_draw
	return view.get_texture().get_image().save_png(path) == OK

func run() -> void:
	var world := load("res://main.tscn").instantiate() as Node3D
	root.add_child(world)
	for tick in 600:
		if world.get("street_block") != null and world.street_block.tracks.size() == 8:
			break
		await physics_frame
	if world.get("street_block") == null or world.street_block.tracks.size() != 8:
		push_error("Street failed to initialize for the cloth comparison")
		quit(1)
		return
	world.hud.hide()
	world.explorer.set_physics_process(false)
	world.street_block.set_physics_process(false)
	var directory := QA.directory()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var modern: bool = world.art_profile.has("washcloth_shader")
	var rows: Array = []
	var nearest: MeshInstance3D
	var distance := INF
	var top_bottom_valid := true
	for instance in world.street_block.find_children("R23_Towel_*", "MeshInstance3D", true, false):
		var cloth := instance as MeshInstance3D
		var mat := cloth.get_active_material(0) as ShaderMaterial
		if modern:
			mat.set_shader_parameter("sample_time", .4)
		var arrays := cloth.mesh.surface_get_arrays(0)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var coords: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
		var highest_hem := -INF
		var lowest_pin := INF
		var pins := 0
		var hem := 0
		for i in vertices.size():
			var height: float = (cloth.global_transform * vertices[i]).y
			if coords[i].y > .999:
				lowest_pin = minf(height, lowest_pin)
				pins += 1
			elif coords[i].y < .001:
				highest_hem = maxf(height, highest_hem)
				hem += 1
		top_bottom_valid = top_bottom_valid and pins > 0 and hem > 0 and lowest_pin - highest_hem > .36
		var center := cloth.global_transform * cloth.get_aabb().get_center()
		if center.distance_to(TARGET) < distance:
			nearest = cloth
			distance = center.distance_to(TARGET)
		rows.append({"mesh": str(cloth.name), "pin_vertices": pins, "hem_vertices": hem,
					 "lowest_pin_m": lowest_pin, "highest_hem_m": highest_hem})
	if nearest == null or not top_bottom_valid:
		quit(1)
		return
	var camera: Camera3D = world.explorer.camera
	var center := nearest.global_transform * nearest.get_aabb().get_center()
	var direction := (EYE - TARGET).normalized()
	camera.global_position = EYE
	camera.look_at(TARGET)
	camera.fov = 67.
	world.explorer._sync_angles()
	var ok := await capture_to(root, directory + "/line.png")
	camera.global_position = center + direction * 1.36 + Vector3.UP * .09
	camera.look_at(center)
	world.explorer._sync_angles()
	camera.fov = 49.
	ok = await capture_to(root, directory + "/fibres.png") and ok
	var report := {"meshes": rows, "nearest": str(nearest.name), "modern": modern}
	if modern:
		var test_view := SubViewport.new()
		test_view.size = Vector2i(640, 640)
		test_view.own_world_3d = true
		test_view.transparent_bg = true
		test_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		root.add_child(test_view)
		var copy := MeshInstance3D.new()
		copy.mesh = nearest.mesh
		test_view.add_child(copy)
		copy.global_transform = nearest.global_transform
		var material := nearest.get_active_material(0).duplicate() as ShaderMaterial
		copy.set_surface_override_material(0, material)
		var sample_camera := Camera3D.new()
		test_view.add_child(sample_camera)
		sample_camera.projection = Camera3D.PROJECTION_ORTHOGONAL
		sample_camera.size = .90
		sample_camera.global_position = center + (direction + Vector3(.55, 0, -.2)).normalized() * 1.8
		sample_camera.look_at(center)
		sample_camera.current = true
		for t in [0., 1.6, 3.2]:
			material.set_shader_parameter("sample_time", t)
			ok = await capture_to(test_view, directory + "/silhouette_%d.png" % int(t * 10.)) and ok
		test_view.queue_free()
	report["passed"] = ok and top_bottom_valid
	QA.decorate(report, world)
	var output := FileAccess.open(directory + "/cotton.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	if ok and modern and "--cloth-perf" in OS.get_cmdline_user_args():
		ok = await measure_clothesline(world, directory)
	quit(0 if ok else 1)

func measure_clothesline(world: Node3D, directory: String) -> bool:
	var stage := SubViewport.new()
	stage.size = Vector2i(1920, 1080)
	stage.own_world_3d = true
	stage.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(stage)
	var models: Array[MeshInstance3D] = []
	var modern_materials: Array[ShaderMaterial] = []
	var old_materials: Array[ShaderMaterial] = []
	for source in world.street_block.find_children("R23_Towel_*", "MeshInstance3D", true, false):
		var item := source as MeshInstance3D
		var center := item.global_transform * item.get_aabb().get_center()
		if center.distance_to(TARGET) > 1.8:
			continue
		var copy := MeshInstance3D.new()
		copy.mesh = item.mesh
		stage.add_child(copy)
		copy.global_transform = item.global_transform
		var scan := item.get_active_material(0).duplicate() as ShaderMaterial
		var old := ShaderMaterial.new()
		old.shader = load("res://shaders/cotton_r23.gdshader")
		old.set_shader_parameter("dye", scan.get_shader_parameter("dye"))
		old.set_shader_parameter("phase", str(item.name).to_int() * .79)
		models.append(copy)
		modern_materials.append(scan)
		old_materials.append(old)
	if models.size() != 5:
		push_error("Unexpected number of towels on the court line: " + str(models.size()))
		return false
	var camera := Camera3D.new()
	stage.add_child(camera)
	camera.global_position = EYE
	camera.look_at(TARGET)
	camera.fov = 67.
	var sun := DirectionalLight3D.new()
	stage.add_child(sun)
	sun.rotation_degrees = Vector3(-42., 27., 0.)
	sun.light_energy = 1.7
	root.disable_3d = true
	world.queue_free()
	await process_frame
	await process_frame
	var rid := stage.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var results := []
	for mode in ["old", "new", "old_repeat"]:
		for index in models.size():
			var mat := modern_materials[index] if mode == "new" else old_materials[index]
			models[index].set_surface_override_material(0, mat)
		for i in 90:
			await RenderingServer.frame_post_draw
		var samples: Array[float] = []
		for i in 240:
			await RenderingServer.frame_post_draw
			samples.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		samples.sort()
		if samples[0] <= 0.:
			return false
		var file := directory + "/cloth1080_" + str(mode) + ".png"
		if stage.get_texture().get_image().save_png(file) != OK:
			return false
		results.append({"mode": mode, "p50_ms": samples[120], "p95_ms": samples[228],
						"samples": samples.size(), "image_sha256": FileAccess.get_sha256(file)})
	var report := {"scope": "Five actual court meshes and materials in an isolated viewport; main city freed",
				   "gpu": RenderingServer.get_video_adapter_name(), "framebuffer": [1920,1080],
				   "meshes": models.size(), "warmup": 90, "passes": results}
	FileAccess.open(directory + "/cloth_gpu.json", FileAccess.WRITE).store_string(JSON.stringify(report, "\t"))
	return true
