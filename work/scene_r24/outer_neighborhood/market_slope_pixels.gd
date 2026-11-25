extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary=layout.plots[1]
	var f: float=-p.depth/2.0
	var eye:=world(p,-p.width*.51,f-7.6,0)
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.fov=71
	camera.position=public_floor([eye.x,-eye.z],p.height+.28)+Vector3.UP*1.56
	camera.look_at(world(p,-p.width*.08,f+.1,3.68))
	camera.make_current()
	await physics_frame
	var hits:=[]
	var meshes:=scene.find_children("*","MeshInstance3D",true,false)
	for pt: Vector2 in [Vector2(1001,380),Vector2(1001,395),Vector2(1001,408),Vector2(975,403),Vector2(975,420),Vector2(626,154)]:
		var screen:=pt*root.get_visible_rect().size/Vector2(1060,596)
		var origin:=camera.project_ray_origin(screen)
		var ray:=camera.project_ray_normal(screen)
		var nearest:=155.0
		var name_hit:=""
		var where:=Vector3.ZERO
		for item: MeshInstance3D in meshes:
			# R22_Bank_Outer discards these outer coordinates in its fragment shader.
			if not item.mesh or not item.is_visible_in_tree() or item.name=="R22_Bank_Outer":continue
			var start:=item.to_local(origin)
			var end:=item.to_local(origin+ray*nearest)
			if item.get_aabb().intersects_segment(start,end)==null:continue
			var dir:=(end-start).normalized()
			var tris:=item.mesh.get_faces()
			for j in range(0,tris.size(),3):
				var hit:Variant=Geometry3D.ray_intersects_triangle(start,dir,tris[j],tris[j+1],tris[j+2])
				if hit!=null:
					var world_hit:=item.to_global(hit)
					var dist:=origin.distance_to(world_hit)
					if dist<nearest:
						nearest=dist
						name_hit=str(item.name)
						where=world_hit
		hits.append({"pixel":[pt.x,pt.y],"mesh":name_hit,"position":[where.x,where.y,where.z],"distance_m":nearest})
	FileAccess.open(output.path_join("market_slope.json"),FileAccess.WRITE).store_string(JSON.stringify(hits,"  "))
	quit()
