extends "res://../../scene_r24/day_one/verify.gd"

var geometry_cache: Dictionary = {}

func from_enu(v: Array) -> Vector3:
	return Vector3(v[0],v[2],-v[1])

func enu(p: Vector3) -> Array:
	return [p.x,-p.z,p.y]

func physics_hits(start: Vector3, direction: Vector3) -> Array:
	var end := start+direction*150.
	var excluded: Array[RID]=[]
	var hits := []
	for i in range(12):
		var r := PhysicsRayQueryParameters3D.create(start,end,1,excluded)
		r.hit_back_faces = true
		var hit := scene.get_world_3d().direct_space_state.intersect_ray(r)
		if hit.is_empty(): break
		excluded.append(hit.rid)
		var body: Node=hit.collider
		hits.append({"mesh":String(body.get_parent().name),"body":String(body.name),
			"point_enu":enu(hit.position),"distance_m":start.distance_to(hit.position),"normal":enu(hit.normal)})
	return hits

func visible_hits(start: Vector3,direction: Vector3, instances: Array[Node]) -> Array:
	var finish := start+direction*150.
	var contacts := []
	for item: MeshInstance3D in instances:
		if not item.mesh or not item.is_visible_in_tree() or String(item.name).begins_with("COLH_"):
			continue
		var inverse := item.global_transform.affine_inverse()
		var local := inverse*start
		var edge := inverse*finish
		if not item.get_aabb().intersects_segment(local,edge):
			continue
		var id := item.mesh.get_instance_id()
		if not geometry_cache.has(id):
			geometry_cache[id]=item.mesh.get_faces()
		var triangles: PackedVector3Array=geometry_cache[id]
		var intersections := []
		var axis := (edge-local).normalized()
		for i in range(0,triangles.size(),3):
			var hit: Variant=Geometry3D.ray_intersects_triangle(local,axis,triangles[i],triangles[i+1],triangles[i+2])
			if hit==null:
				continue
			var p: Vector3=item.global_transform*hit
			var n := (triangles[i+1]-triangles[i]).cross(triangles[i+2]-triangles[i]).normalized()
			intersections.append({"mesh":String(item.name),"path":str(item.get_path()),
				"point_enu":enu(p),"distance_m":start.distance_to(p),
				"normal":enu((inverse.basis.transposed()*n).normalized())})
		intersections.sort_custom(func(a:Dictionary,b:Dictionary)->bool:return a.distance_m<b.distance_m)
		contacts.append_array(intersections.slice(0,4))
	contacts.sort_custom(func(a:Dictionary,b:Dictionary)->bool:return a.distance_m<b.distance_m)
	return contacts.slice(0,9)

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	root.size=Vector2i(900,506)
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	var specs_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--scene-ray-input="):
			specs_path=arg.trim_prefix("--scene-ray-input=")
	var specs: Array=JSON.parse_string(FileAccess.get_file_as_string(specs_path))
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.make_current()
	var meshes := scene.find_children("*","MeshInstance3D",true,false)
	for spec: Dictionary in specs:
		camera.global_position=from_enu(spec.eye_enu)
		camera.look_at(from_enu(spec.target_enu))
		camera.fov=spec.fov_deg
		await process_frame
		var results := []
		for pixel: Array in spec.pixels:
			var v := tan(deg_to_rad(camera.fov*.5))
			var x := ((float(pixel[0])+.5)/900.*2.-1.)*v*900./506.
			var y := (1.-(float(pixel[1])+.5)/506.*2.)*v
			var dir := (camera.global_basis*Vector3(x,y,-1.)).normalized()
			spec["viewport_size_reported"]=[root.size.x,root.size.y]
			spec["projection_size"]=[900,506]
			results.append({"pixel":pixel,"physics":physics_hits(camera.global_position,dir),
				"geometry":visible_hits(camera.global_position,dir,meshes)})
		spec["hits"]=results
	FileAccess.open(output.path_join("rays.json"),FileAccess.WRITE).store_string(JSON.stringify(specs,"  "))
	print("CQ_SCENE_RAYS ",specs.size())
	quit()
