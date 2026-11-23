extends Node3D

var camera := Camera3D.new()
var bounds := AABB()
var report := {}
var folder := ProjectSettings.globalize_path("res://../captures/")
var items: Array[MeshInstance3D] = []

func _ready() -> void:
	var gltf := GLTFDocument.new()
	var data := GLTFState.new()
	var asset_file := "dazu_model.glb"
	if "--alley" in OS.get_cmdline_user_args():
		asset_file = "alley_scan.glb"
		folder = ProjectSettings.globalize_path("res://../alley_captures/")
	var path := ProjectSettings.globalize_path("res://../").path_join(asset_file)
	var error := gltf.append_from_file(path, data)
	if error != OK:
		push_error("Could not open the source GLB: %d" % error)
		get_tree().quit(1)
		return
	var imported := gltf.generate_scene(data)
	add_child(imported)
	var triangles := 0
	for node in imported.find_children("*", "MeshInstance3D", true, false):
		var item := node as MeshInstance3D
		var box := item.global_transform * item.get_aabb()
		bounds = box if items.is_empty() else bounds.merge(box)
		items.append(item)
		for i in item.mesh.get_surface_count():
			var arrays := item.mesh.surface_get_arrays(i)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			triangles += (indices.size() if not indices.is_empty() else vertices.size()) / 3
	if items.is_empty() or bounds.size.length() < .001:
		push_error("Imported file has no measurable mesh")
		get_tree().quit(1)
		return
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(.23, .25, .27)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = .95
	var environment := WorldEnvironment.new()
	environment.environment = env
	add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-56, -35, 0)
	sun.light_energy = .45
	add_child(sun)
	add_child(camera)
	var center := bounds.get_center()
	var extent := maxf(bounds.size.x, bounds.size.z)
	camera.near = maxf(.015, extent / 200000.)
	camera.far = maxf(200., bounds.size.length() * 6.)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = extent * 1.12
	camera.global_position = center + Vector3.UP * bounds.size.length() * 1.5
	camera.look_at(center, Vector3.FORWARD)
	camera.current = true
	DirAccess.make_dir_recursive_absolute(folder)
	report = {"engine": Engine.get_version_info().string, "source_sha256": FileAccess.get_sha256(path),
			  "bounds_min": [bounds.position.x,bounds.position.y,bounds.position.z],
			  "bounds_size": [bounds.size.x,bounds.size.y,bounds.size.z],
			  "mesh_instances": items.size(), "rendered_triangles": triangles, "cameras": []}
	var success := await photo("map")
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 55.
	camera.global_position = center + Vector3(.62,.67,.80) * extent
	camera.look_at(center)
	success = await photo("overview") and success
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--eye="):
			var values := arg.trim_prefix("--eye=").split(",")
			if values.size() != 6 and values.size() != 7:
				get_tree().quit(2)
				return
			var result := await eye(values)
			success = result and success
	FileAccess.open(folder.path_join("review.json"), FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	if "--capture" in OS.get_cmdline_user_args() or not success:
		get_tree().quit(0 if success else 1)

func eye(values: PackedStringArray) -> bool:
	if not has_node("TemporaryProbeCollision"):
		var physics := StaticBody3D.new()
		physics.name = "TemporaryProbeCollision"
		add_child(physics)
		for item in items:
			var shape := item.mesh.create_trimesh_shape()
			if shape == null:
				continue
			shape.backface_collision = true
			var holder := CollisionShape3D.new()
			holder.shape = shape
			physics.add_child(holder)
			holder.global_transform = item.global_transform
		for i in 3:
			await get_tree().physics_frame
	var x := values[1].to_float()
	var z := values[2].to_float()
	var start := Vector3(x,bounds.end.y + 20.,z)
	var query := PhysicsRayQueryParameters3D.create(start, Vector3(x,bounds.position.y - 20.,z))
	query.hit_back_faces = true
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		push_error("No surface at " + str(Vector2(x,z)))
		return false
	var height := values[5].to_float()
	var offset_z := values[6].to_float() if values.size() == 7 else 0.
	camera.global_position = hit.position + Vector3.UP * height + Vector3.BACK * offset_z
	camera.fov = 66.
	var direction := Vector3(values[3].to_float(),-.045,values[4].to_float()).normalized()
	camera.look_at(camera.global_position + direction)
	report[values[0]] = {"surface_y":hit.position.y, "eye_offset_in_asset_units":height,"z_offset_from_probe":offset_z}
	return await photo(values[0])

func photo(label: String) -> bool:
	for i in 8:
		await RenderingServer.frame_post_draw
	var frame := get_viewport().get_texture().get_image()
	var path := folder.path_join(label + ".png")
	if frame == null or frame.save_png(path) != OK:
		return false
	report.cameras.append({"name":label,"position":str(camera.global_position),"sha256":FileAccess.get_sha256(path)})
	return true
