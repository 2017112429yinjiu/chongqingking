extends "../../continuous_site_walk.gd"

func enu_list(p: Vector3) -> Array:
	return [p.x,-p.z,p.y]

func world_point(en: Array, elevation: float) -> Vector3:
	return Vector3(en[0],elevation,-en[1])

func trace(from: Vector3, to: Vector3, limit := 12) -> Array:
	var results: Array=[]
	var exclusions: Array[RID]=[]
	var space: PhysicsDirectSpaceState3D=scene.get_world_3d().direct_space_state
	for i in limit:
		var query:=PhysicsRayQueryParameters3D.create(from,to,1,exclusions)
		query.hit_back_faces=true
		var hit:=space.intersect_ray(query)
		if hit.is_empty(): break
		exclusions.append(hit.rid)
		results.append({"body":str(hit.collider.get_parent().name),"at":enu_list(hit.position),"normal":enu_list(hit.normal)})
	return results

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	graphics=DisplayServer.get_name()!="headless"
	RenderingServer.render_loop_enabled=false
	var path: String=""
	for option in OS.get_cmdline_user_args():
		if option.begins_with("--rail-guide="): path=option.trim_prefix("--rail-guide=")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not plan.has("samples"):
		push_error("Missing rail survey samples")
		quit(2)
		return
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(25)
	if not graphics:
		var points: Dictionary={}
		for family in plan.samples:
			var locations: Array=[]
			for p in plan.samples[family]:
				var high:=world_point(p,100.)
				var low:=world_point(p,-30.)
				locations.append({"en":p,"down":trace(high,low),"up":trace(low,high)})
			points[family]=locations
		var owners: Array=[]
		for item: MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
			var name:=str(item.name)
			if not name.to_lower().contains("rail") and not name.to_lower().contains("nanjimen"): continue
			var box: AABB=item.global_transform*item.get_aabb()
			if box.end.x< -148. or box.position.x> -85. or box.position.z>198. or box.end.z<39.: continue
			owners.append({"name":name,"visible":item.is_visible_in_tree(),"corner_a":enu_list(box.position),"corner_b":enu_list(box.end),"parent":str(item.get_parent().name)})
		FileAccess.open(output.path_join("profiles.json"),FileAccess.WRITE).store_string(JSON.stringify({"samples":points,"inventory_near_north_span":owners,"identity":scene.scene_identity.district_500,"grade_install":scene.scene_identity.get("nanqu_grade",{})},"  "))
		quit(0)
		return
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED
	scene.hud.hide()
	var camera:=Camera3D.new()
	camera.keep_aspect=Camera3D.KEEP_HEIGHT
	camera.cull_mask=scene.explorer.camera.cull_mask
	scene.add_child(camera)
	camera.current=true
	for layer in ["HUD","Hud","UI"]:
		var overlay:=scene.get_node_or_null(layer)
		if overlay is CanvasItem: overlay.hide()
	var hillside_trees := scene.find_children("NanquLandside_Tree_*", "Node3D", true, false)
	var views: Array=[]
	for v: Dictionary in plan.views:
		for tree: Node3D in hillside_trees:
			tree.visible = not v.get("bank_only", false)
		camera.fov=v.fov_deg
		camera.global_position=world_point(v.eye_enu,v.eye_enu[2])
		camera.look_at(world_point(v.target_enu,v.target_enu[2]))
		camera.reset_physics_interpolation()
		camera.force_update_transform()
		await frames(3)
		RenderingServer.force_draw(false,1.0/60.0)
		var frame:=root.get_texture().get_image()
		var error:=frame.save_png(output.path_join(v.id+".png"))
		var projection:=camera.get_camera_projection()
		var view:=Projection(camera.get_camera_transform().affine_inverse())
		var columns := func(m: Projection) -> Array:
			return [[m.x.x,m.x.y,m.x.z,m.x.w],[m.y.x,m.y.y,m.y.z,m.y.w],[m.z.x,m.z.y,m.z.z,m.z.w],[m.w.x,m.w.y,m.w.z,m.w.w]]
		views.append({"id":v.id,"view_columns":columns.call(view),"projection_columns":columns.call(projection),"pixels":[frame.get_width(),frame.get_height()],"write_code":error})
		check(v.id,error==OK)
	FileAccess.open(output.path_join("matrices.json"),FileAccess.WRITE).store_string(JSON.stringify(views,"  "))
	quit(2 if ever_failed else 0)
