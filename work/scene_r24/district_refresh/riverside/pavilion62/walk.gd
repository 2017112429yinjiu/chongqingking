extends "../survey.gd"
## Check the doorway, park paving and the street return with the actual explorer.

const ROUTES := {
	"park_to_door":[[-19.,-188.68],[-16.2,-188.76],[-14.02,-188.94],
		[-12.79,-189.19],[-12.68,-190.28],[-12.79,-191.31]],
	"street_return":[[-12.79,-189.18],[-12.69,-187.94],[-12.72,-186.68],[-12.61,-185.65]],
}

func verify() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene = scene
	while not scene.get("gameplay"):
		await physics_frame
	await frames(24)
	if DisplayServer.get_name() != "headless":
		await capture_pavilion()
		quit()
		return
	check("legacy_plot_62_released",scene.find_child("COL_Outer500_Frame_62",true,false)==null)
	var space := scene.get_world_3d().direct_space_state
	var profiles := {}
	for label: String in ROUTES:
		var path: Array[Vector3] = []
		var profile := []
		for station: Array in ROUTES[label]:
			var base := ground_point(station,0.0)
			var ray := PhysicsRayQueryParameters3D.create(base+Vector3.UP*.87,base-Vector3.UP*1.1,1)
			var hit := space.intersect_ray(ray)
			assert(not hit.is_empty(),str(station))
			path.append(hit.position+Vector3.UP*.04)
			profile.append({"east_north":station,"height":hit.position.y,"support":String(hit.collider.get_parent().name)})
		profiles[label]=profile
		await walk_pair(label,path)
	check("door_supported_by_real_structure",String(profiles.park_to_door[-1].support).contains("registered_body"))
	FileAccess.open(output.path_join("pavilion_62.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"checks":checks,"walks":walks,"profiles":profiles},"  "))
	quit(2 if ever_failed else 0)

func capture_pavilion() -> void:
	scene.hud.hide()
	root.use_occlusion_culling = false
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.fov = 67.0
	camera.far = 215.0
	camera.make_current()
	var views := [
		["field_side",[-18.42,-181.34],[-12.06,-193.67],2.0],
		["garden_threshold",[-18.7,-188.66],[-12.68,-190.32],1.38],
		["look_back_toward_street",[-12.79,-191.31],[-12.61,-185.65],1.20],
	]
	if "--qa-pavilion62-return-view" in OS.get_cmdline_user_args():
		views = [views[-1]]
	var stations := []
	for item: Array in views:
		var eye := ground_point(item[1],1.63)
		var aim := ground_point(item[2],float(item[3]))
		camera.global_position = eye
		camera.look_at(aim)
		await process_frame
		RenderingServer.force_draw(false,1.0/60.0)
		var status := root.get_texture().get_image().save_png(output.path_join(item[0]+".png"))
		assert(status == OK)
		stations.append({"id":item[0],"eye_xyz":[eye.x,eye.y,eye.z],"aim_xyz":[aim.x,aim.y,aim.z]})
	FileAccess.open(output.path_join("cameras.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"scene":scene.scene_file_path,"stations":stations,"size":str(root.size),
		"renderer":RenderingServer.get_current_rendering_method(),"adapter":RenderingServer.get_video_adapter_name(),
	}, "  "))
