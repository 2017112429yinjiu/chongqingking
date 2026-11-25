extends "../../scene_r24/street_blocks/views.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(24)
	var geo: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://source_data/geo_layout.json"))
	var trace: Array=geo.paths.filter(func(s):return int(s.id)==734116601)[0].points
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.position=terrain(trace[7])+Vector3.UP*1.62
	camera.look_at(terrain([-228.,160.])+Vector3.UP*2.25)
	camera.fov=71
	camera.make_current()
	await frames(3)
	var res:=root.get_visible_rect().size
	var records: Array=[]
	for q: Vector2 in [Vector2(679,193),Vector2(761,186),Vector2(507,210)]:
		var target:=q*res/Vector2(1060,596)
		var start:=camera.project_ray_origin(target)
		var ray:=camera.project_ray_normal(target)
		var hits:=RenderingServer.instances_cull_ray(start,start+ray*600.,scene.get_world_3d().scenario)
		for id in hits:
			var obj:=instance_from_id(id) as GeometryInstance3D
			if not obj or not obj.is_visible_in_tree():continue
			var aabb:=obj.global_transform*obj.get_aabb()
			if aabb.size.length()>180:continue
			var p:=aabb.get_center()
			var screen:=camera.unproject_position(p)*Vector2(1060,596)/res
			if screen.distance_to(q)>160:continue
			records.append({"point":str(q),"name":str(obj.name),"parent":str(obj.get_parent().name),"center":str(p),"size":str(aabb.size)})
	FileAccess.open(output.path_join("sightline.json"),FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	quit()
