extends "survey.gd"

# Supplement facade-normal stations with positions already reached by the stock controller.
func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(24)
	RenderingServer.render_loop_enabled=false
	scene.hud.hide()
	cam=Camera3D.new()
	scene.add_child(cam)
	cam.make_current()
	var feet:Array=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_FEET")))
	var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_OUTLINES")))
	var surveyed:Dictionary={}
	for item:Dictionary in manifest.views:
		var key:String=item.key
		if not key.begins_with("outline_"):continue
		var id:=key.get_slice("_",key.get_slice_count("_")-1)
		if surveyed.has(id):continue
		surveyed[id]=true
		var target:=vec(item.target)
		var best_eye:=Vector3.ZERO
		var best_score:=INF
		for foot:Array in feet:
			var eye:=vec(foot)+Vector3.UP*1.6
			var delta:=eye-target
			var distance:=Vector2(delta.x,delta.z).length()
			if distance<4. or distance>250.:continue
			var cost:=distance+1.8*absf(delta.y)+maxf(0.,8.-distance)*2.
			if cost>=best_score:continue
			var ray:=PhysicsRayQueryParameters3D.create(eye,target,1)
			var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
			if hit and eye.distance_to(hit.position)<eye.distance_to(target)*.82:cost+=85.
			if cost<best_score:
				best_score=cost
				best_eye=eye
		if best_score==INF:continue
		await picture("roadview_"+id,"实走路位看轮廓 "+id,best_eye,target)
	write_json("views.json",{"views":views})
	quit()
