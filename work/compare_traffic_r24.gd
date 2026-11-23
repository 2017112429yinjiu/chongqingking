extends SceneTree

func _initialize() -> void:call_deferred("capture")

func capture() -> void:
	var world:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(world)
	while world.street_block==null or world.street_block.tracks.size()!=8:await physics_frame
	var block: Node3D=world.street_block
	block.set_physics_process(false)
	world.hud.hide()
	var directory:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/traffic")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var observations: Array=[]
	for setup in [
			["beneath_bridge",Vector3(43.2,10.76,80.3),Vector3(62.3,11.0,87.05),63.4,60.0],
			["junction",Vector3(25.3,10.84,78.8),Vector3(40.0,8.4,89.9),41.0,44.5],
			["curb",Vector3(51.25,11.17,81.0),Vector3(60.8,9.04,87.3),61.6,55.5]]:
		var done: Dictionary={}
		var camera: Camera3D=world.explorer.camera
		world.explorer.automation_axis=Vector2.ZERO
		camera.global_position=setup[1];camera.look_at(setup[2]);world.explorer._sync_angles()
		camera.fov=65.
		for t in block.tracks:
			if not t.car:continue
			var near_x: float=setup[3] if t.route=="west" else setup[4]
			var wanted: float=near_x if not done.has(t.route) else near_x+(-22.0 if t.route=="west" else 23.)
			var curve: Curve3D=block.routes[t.route]
			var error:=INF
			for i in ceili(curve.get_baked_length()/.1)+1:
				var point:=curve.sample_baked(i*.1)
				if absf(point.x-wanted)<error:
					error=absf(point.x-wanted);t.d=minf(i*.1,curve.get_baked_length())
			block._pose(t,0.,true)
			done[t.route]=true
		for f in 24:await RenderingServer.frame_post_draw
		var im:=root.get_texture().get_image()
		if im.save_png(directory+"/"+str(setup[0])+".png")!=OK:quit(2);return
		var ground:=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(camera.global_position,camera.global_position-Vector3.UP*5,1))
		observations.append({"view":setup[0],"eye":str(camera.global_position),"ground_below_eye_m":camera.global_position.y-ground.position.y if not ground.is_empty() else null,"floor":str(ground.collider.get_parent().name) if not ground.is_empty() else ""})
	var report:={"poses":observations,"mode":"Stopped traffic at matching horizontal positions; fixed camera and field of view"}
	preload("res://scripts/qa_context.gd").decorate(report,world)
	FileAccess.open(directory+"/traffic_cameras.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	quit()

