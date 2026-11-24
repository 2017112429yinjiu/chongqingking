extends "../../scene_r24/day_one/verify.gd"
func v(x:float,y:float,z:float)->Vector3:return Vector3(x,y,z)
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	await frames(25)
	check("composition",scene.scene_identity.district_connections.missing.is_empty(),scene.scene_identity.district_connections.missing)
	var camera:=Camera3D.new()
	scene.add_child(camera);camera.current=true
	camera.fov=66
	var views:=[
		["01_back_door",v(-85,18.72,10.02),v(-83.69,18.80,9.18)],
		["02_turn_below",v(-84.9,22.11,17.04),v(-84.85,19.72,12.06)],
		["03_upper_flight",v(-82.6,25.52,9.87),v(-83.18,21.36,16.88)],
		["04_under_shelter",v(-4.16,17.5,28.83),v(-1.17,16.32,28.82)],
		["05_court_bank",v(-18.79,21.31,2.55),v(-22.15,20.28,1.71)],
		["06_paint",v(-40.55,21.16,-9.9),v(-36.70,20.53,-6.68)],
		["07_service_front",v(-6.82,23.98,-12.58),v(3.9,23.38,-12.50)],
		["08_service_back",v(26.1,25.48,-21.5),v(23.9,23.25,-12.6)],
		["09_ac_ten",v(-56.2,23.33,-22.40),v(-57.85,23.23,-16.92)],
		["10_rack_paving",v(-37.8,18.34,21.55),v(-37.6,17.00,18.50)],
		["11_east_steps",v(49.1,23.63,-1.88),v(46.54,22.43,-2.23)],
		["12_bridge_exit",v(-79.2,25.52,14.35),v(-66.5,25.37,14.35)],
		["13_west_junction",v(-70.0,18.83,11.96),v(-73.2,17.55,8.)]]
	for row:Array in views:
		camera.global_position=row[1];camera.look_at(row[2])
		await frames(6)
		await capture(row[0])
	var hit_names:={}
	var low:=INF;var high:=-INF
	for i in 65:
		for j in 9:
			var p:=v(-41.5+15.*j/8.,20.83,-13.+26.*i/64.)
			var hit:=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(p,p-Vector3.UP*.7,1))
			if hit.is_empty():hit_names["missing"]=true;continue
			low=minf(low,hit.position.y);high=maxf(high,hit.position.y);hit_names[str(hit.collider.get_parent().name)]=true
	check("paint_entirely_flat",hit_names.size()==1 and hit_names.has("COL_Community_court_pavement") and high-low<.0001,[low,high,hit_names.keys()])
	FileAccess.open(output.path_join("sites.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
