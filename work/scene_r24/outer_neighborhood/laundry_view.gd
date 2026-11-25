extends "../../scene_r24/outer_neighborhood/survey.gd"

# Trace the same registered R6 pixels through visible graphics meshes, including
# uncollidable rails. A physics ray alone missed both intruding objects.
func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for step in 1600:
		if scene.get("gameplay"): break
		await physics_frame
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary=layout.plots[4]
	assert(p.plot_id==4 and p.room.use=="washroom")
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.fov=71
	camera.position=world(p,p.room.jamb_u,p.room.door_v,1.63)
	camera.look_at(world(p,p.room.inside_u,-p.depth/2.0+1.32,.89))
	camera.make_current()
	await physics_frame
	var records: Array=[]
	var failed:=false
	for pixel: Vector2 in [Vector2(777,435),Vector2(805,402),Vector2(831,371),Vector2(744,168),Vector2(750,170)]:
		var screen:=pixel*root.get_visible_rect().size/Vector2(1060,596)
		var origin:=camera.project_ray_origin(screen)
		var direction:=camera.project_ray_normal(screen)
		var nearest:=18.0
		var owner:=""
		for item: MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
			if not item.is_visible_in_tree() or not item.mesh: continue
			var local:=item.to_local(origin)
			var end:=item.to_local(origin+direction*nearest)
			if item.get_aabb().intersects_segment(local,end)==null: continue
			var ray:=(end-local).normalized()
			var tris:=item.mesh.get_faces()
			for i in range(0,tris.size(),3):
				var hit: Variant=Geometry3D.ray_intersects_triangle(local,ray,tris[i],tris[i+1],tris[i+2])
				if hit!=null:
					var dist:=origin.distance_to(item.to_global(hit))
					if dist<nearest:
						nearest=dist
						owner=str(item.name)
		records.append({"pixel":str(pixel),"first_mesh":owner,"distance_m":nearest})
		if owner.is_empty() or owner in ["R24_LinkRail_R24_link_painted_rail","Outer500_LaundryRailReturn","Outer500_Street_furniture"]:
			failed=true
	FileAccess.open(output.path_join("laundry_pixels.json"),FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	quit(2 if failed else 0)
