extends "../../scene_r24/shancheng_courts/delivery_take.gd"

func verify_tool_bay(district:Node3D, service:Vector3, inward:Vector3) -> void:
	var scenario: Dictionary = district.get_meta("acceptance_player_points")
	var at := point(scenario["00-tool-eye"][0])
	var actor: CharacterBody3D = scene.explorer.body
	var open_lane := service + inward*1.20
	var visit := await WalkTest._walk(scene,[open_lane,at],"service_to_reachable_tool_eye")
	var actual := actor.global_position
	var space := scene.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	var hits: Array = []
	for delta:Vector3 in [Vector3.ZERO,Vector3.FORWARD*.20,Vector3.BACK*.20,Vector3.LEFT*.20,Vector3.RIGHT*.20]:
		var probe:=at+delta
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(probe + Vector3.UP*.25,probe-Vector3.UP*.35,1))
		if not hit.is_empty():
			hits.append({"height_m":hit.position.y,"mesh":str(hit.collider.get_parent().name)})
	check("tool_eye_reached_on_workshop_floor",visit["pass"] and actual.distance_to(at)<.33 and hits.size()==5,
		{"movement":visit,"eye_foot":[at.x,-at.z,at.y],"actual_foot":[actual.x,-actual.z,actual.y],"supports":hits})
	var materials: Array = []
	var layer := district.get_node("Acceptance_south")
	var parts := layer.find_children("Review00_*","MeshInstance3D",true,false)
	for part: MeshInstance3D in parts:
		for i:int in part.mesh.get_surface_count():
			var arrays := part.mesh.surface_get_arrays(i)
			var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
			var finish := part.mesh.surface_get_material(i) as BaseMaterial3D
			materials.append({"mesh":str(part.name),"material":finish.resource_name,"uv":uv.size(),
				"albedo":finish.albedo_texture.resource_path if finish.albedo_texture else "",
				"normal":finish.normal_texture.resource_path if finish.normal_enabled and finish.normal_texture else "",
				"roughness":finish.roughness_texture.resource_path if finish.roughness_texture else ""})
	check("workshop_parts_have_runtime_uv_and_pbr",parts.size()==5 and materials.size()>=7 and materials.all(
		func(row): return row.uv>0 and not row.albedo.is_empty() and not row.normal.is_empty() and not row.roughness.is_empty()),
		materials)
	var back := await WalkTest._walk(scene,[open_lane,service],"tool_eye_to_service")
	check("return_from_tool_eye",back["pass"],back)

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
	if "--qa-repair-tool-eye" in OS.get_cmdline_user_args():
		await verify_tool_bay(scene.get_node("City/OuterDistrict500"),point(site.service),inward)
	var yard:=await WalkTest._walk(scene,[point(site.rear),point(site.court)],"workshop_to_court")
	check("reach_inner_court",yard["pass"],yard)
	var back:=await WalkTest._walk(scene,[point(site.rear),point(site.service),point(site.porch),point(site.street)],"return_to_same_street")
	check("walk_back_from_court",back["pass"],back)
	check("back_at_start",actor.global_position.distance_to(point(site.street))<.65,str(actor.global_position))
	recording=false
	FileAccess.open(output.path_join("walk.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"physics_hz":Engine.physics_ticks_per_second,"ticks_per_image":9,"images":saved_frames},"  "))
	quit(2 if ever_failed else 0)
