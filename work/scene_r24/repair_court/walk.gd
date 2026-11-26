extends "../../scene_r24/shancheng_courts/delivery_take.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	var graphics:=DisplayServer.get_name()!="headless"
	if graphics: RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	while not scene.get("gameplay"): await physics_frame
	await frames(32)
	var site: Dictionary=scene.get_node("City/OuterDistrict500").get_meta("repair_court")
	var actor=scene.explorer.body
	var bike=scene.gameplay.scooter
	var parked_at: Vector3=bike.global_position
	var wallet: int=scene.gameplay.earnings
	check("start_on_734116598",actor.global_position.distance_to(point(site.street))<.6,str(actor.global_position))
	check("underinflated_scooter_parked",bike.parked and bike.tyre_pressure<1.5,str(bike.global_position))
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary=layout.plots.filter(func(entry): return entry.plot_id==0)[0]
	var axis:=Vector3(cos(p.bearing),0,-sin(p.bearing))
	var inward:=Vector3(-sin(p.bearing),0,-cos(p.bearing))
	var section: Array=[]
	for i in int(site.risers):
		for side: float in [-1.30,0.0,1.30]:
			var at:=point(site.toe)+inward*(i+.5)*float(site.going_m)+axis*side
			var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*1.65,at-Vector3.UP*.65,1)
			var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
			section.append({"step":i,"offset":side,"support":str(hit.collider.get_parent().name) if hit else "missing"})
	check("all_stone_treads_exposed_across_lane",section.all(func(h): return h.support.begins_with("COL_Outer500_RepairCourt")),section)
	if graphics:
		recording=true
		record_tick()
	var visit:=await WalkTest._walk(scene,[point(site.porch),point(site.service)],"public_walk_to_repair_counter")
	check("walk_in_through_front",visit["pass"],visit)
	var target=scene.gameplay.manager.select()
	check("workbench_within_reach",target!=null and target.interaction_id=="workshop.tyre",str(target))
	tap(KEY_E)
	await frames(18)
	check("E_inflates_player_scooter",is_equal_approx(bike.tyre_pressure,bike.FULL_PRESSURE),bike.tyre_pressure)
	tap(KEY_E)
	await frames(12)
	check("repeat_check_preserves_bike_and_wallet",bike.parked and bike.global_position.distance_to(parked_at)<.20 and scene.gameplay.earnings==wallet)
	var yard:=await WalkTest._walk(scene,[point(site.rear),point(site.court)],"workshop_to_court")
	check("reach_inner_court",yard["pass"],yard)
	var back:=await WalkTest._walk(scene,[point(site.rear),point(site.service),point(site.porch),point(site.street)],"return_to_same_street")
	check("walk_back_from_court",back["pass"],back)
	check("back_at_start",actor.global_position.distance_to(point(site.street))<.65,str(actor.global_position))
	recording=false
	FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"physics_hz":Engine.physics_ticks_per_second,"ticks_per_image":9,"images":saved_frames},"  "))
	quit(2 if ever_failed else 0)
