extends "../../scene_r24/day_one/verify.gd"
const Unit=preload("res://scripts/unit_interior.gd")
var route:Node3D
var floors:Dictionary={}
var expected:={"lower_court":16.44,"unit_landing":19.89,"back_alley":17.3,"blue_entrance":17.12,"blue_half":20.52,"upper_window":23.92,"bridge_middle":23.92,"home_301":22.90}
var take_dir:=""
var take_tick:=0
var take_count:=0
func record_frame()->void:
	take_tick+=1
	if take_tick%4!=0:return
	RenderingServer.force_draw(false,1./60.)
	var path:=take_dir.path_join("walk_%05d.jpg"%take_count)
	if root.get_texture().get_image().save_jpg(path,.89)!=OK:
		push_error("Cannot record native frame")
	take_count+=1
func station(id:String)->bool:
	var y:float=game.actor.body.global_position.y
	floors[id]=y
	return check(id+"_floor",game.actor.body.is_on_floor() and absf(y-float(expected[id]))<.35,y)
func face(point:Vector3)->void:
	game.actor.camera.look_at(point)
	game.actor._sync_angles()
	await frames(6)
func shot(label:String,point:Vector3)->void:
	await face(point)
	await capture(label)
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	for i in 1500:
		if scene.gameplay:break
		await physics_frame
	game=scene.gameplay
	if not check("world",game!=null):end_run();return
	await frames(32)
	lesson=game.lesson
	route=game.passage
	if not check("practice_isolated",route!=null and route.stage==route.Stage.COLLECT and lesson.record_path.is_empty() and game.earnings==24):end_run();return
	lesson.record_path=output.path_join("shift.cfg")
	check("all_donor_meshes_found",scene.scene_identity.district_connections.missing.is_empty(),scene.scene_identity.district_connections.missing)
	if "--take" in OS.get_cmdline_user_args():
		take_dir=output.path_join("take")
		DirAccess.make_dir_recursive_absolute(take_dir)
		physics_frame.connect(record_frame)
	await shot("01_lower_gate",Vector3(-54.9,17.85,19.5))
	if not await walk([Vector3(-54.9,16.44,19.5)],"cross_lower_gate"):end_run();return
	station("lower_court")
	if not await walk([Unit.LANDING],"climb_unit_one"):end_run();return
	station("unit_landing")
	if not await walk([Vector3(-62.15,19.89,19.05),Vector3(-62.15,19.89,14.6),Vector3(-62.54,19.89,14.56)],"find_cook_202"):end_run();return
	await shot("02_pickup_202",route.pickup.global_position)
	tap(KEY_E)
	if not check("take_douhua",route.stage==route.Stage.CARRY and game.order==game.Order.CARRYING and game.earnings==24):end_run();return
	await frames(15)
	tap(KEY_E)
	check("202_is_not_recipient",not game.free_answered and game.earnings==24)
	if not await walk([Vector3(-62.48,19.89,8.12),Vector3(-65.34,19.89,8.04),Vector3(-70.65,17.3,8.04)],"leave_via_back_stairs"):end_run();return
	station("back_alley")
	await shot("03_back_alley",Vector3(-84.85,19.27,8.98))
	if not await walk([Vector3(-74.2,17.38,7.2),Vector3(-78.36,17.75,4.90),Vector3(-84.85,17.57,5.74)],"turn_at_blue_corner"):end_run();return
	await shot("03b_blue_door",Vector3(-84.85,18.45,9.12))
	if not await walk([Vector3(-84.85,17.4,7.25),Vector3(-84.83,17.12,9.75)],"blue_tile_alley_door"):end_run();return
	station("blue_entrance")
	await shot("04_blue_stair",Vector3(-84.85,21.64,17.35))
	if not await walk([Vector3(-84.84,20.52,17.02)],"climb_to_turn"):end_run();return
	station("blue_half")
	if not await walk([Vector3(-82.59,20.52,17.03),Vector3(-82.59,23.92,9.84)],"reverse_flight_to_window"):end_run();return
	station("upper_window")
	await shot("05_upper_window",Vector3(-83.10,25.33,9.04))
	if not await walk([Vector3(-80.3,23.92,9.89),Vector3(-80.22,23.92,14.34),Vector3(-77.81,23.92,14.36)],"enter_high_crossing"):end_run();return
	await shot("06_crossing",Vector3(-66.0,25.12,14.30))
	if not await walk([Vector3(-72.1,23.92,14.36)],"cross_above_alley"):end_run();return
	station("bridge_middle")
	await shot("06b_blue_landing",Vector3(-80.1,25.08,14.30))
	await shot("07_down_to_alley",Vector3(-70.7,17.8,8.1))
	lesson._save()
	DirAccess.copy_absolute(lesson.record_path,output.path_join("bridge.cfg"))
	if not await walk([Vector3(-65.68,23.92,14.34),Vector3(-61.2,22.90,14.34)],"cross_into_original_house_and_descend"):end_run();return
	station("home_301")
	await shot("08_door_301",route.DOOR)
	if not await walk([Vector3(-59.30,22.90,14.14)],"knock_at_301"):end_run();return
	await face(route.DOOR)
	tap(KEY_E)
	check("recipient_answers",game.free_answered and game.earnings==24 and game.destination.global_position.distance_to(route.SHELF+Vector3.UP*.12)<.01)
	if not await walk([Vector3(-59.26,22.90,14.94)],"reach_301_ledge"):end_run();return
	await face(game.destination.global_position)
	tap(KEY_E)
	await frames(35)
	check("pay_only_after_release",game.shelf_time>=0. and game.earnings==24)
	await capture("09_placing")
	await frames(65)
	tap(KEY_E)
	check("order_paid_once",route.stage==route.Stage.IDLE and game.earnings==40 and game.delivered_count==4 and game.bag.global_position.distance_to(route.SHELF)<.01)
	await capture("10_received")
	if physics_frame.is_connected(record_frame):physics_frame.disconnect(record_frame)
	# Walk the new crossing and both switchbacks in the opposite direction without a spawn reset.
	if not await walk([Vector3(-63.0,22.90,14.34),Vector3(-66.4,23.92,14.34),Vector3(-80.25,23.92,14.34),Vector3(-80.25,23.92,9.88),Vector3(-82.60,23.92,9.86),Vector3(-82.60,20.52,17.03),Vector3(-84.85,20.52,17.03),Vector3(-84.85,17.12,9.65),Vector3(-84.85,17.3,8.12)],"return_to_back_lane"):end_run();return
	end_run()
func end_run()->void:
	var result:={"checks":checks,"floors":floors,"native_frames_15fps":take_count}
	FileAccess.open(output.path_join("route.json"),FileAccess.WRITE).store_string(JSON.stringify(result,"\t"))
	quit(2 if ever_failed else 0)
