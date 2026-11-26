extends "../../scene_r24/day_one/verify.gd"

const SHORT := {"南区路车棚修理铺":"repair", "照相巷便民市场":"market", "江岸茶摊":"tea"}
const DOORS := {"repair":0.0, "market":-0.78, "tea":-1.65}

func world(p: Dictionary, u: float, v: float, z: float) -> Vector3:
	var a: float = p.bearing
	var xy: Array = p.east_north
	return Vector3(xy[0]+cos(a)*u-sin(a)*v, p.height+z, -xy[1]-sin(a)*u-cos(a)*v)

func shot(label: String, eye: Vector3, target: Vector3) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.position=eye
	camera.look_at(target)
	camera.fov=71
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var code:=root.get_texture().get_image().save_png(output.path_join(label+".png"))
	assert(code==OK)
	camera.queue_free()

func trial(label: String,points: Array,both: bool=true) -> void:
	scene.explorer.begin_route_test(points[0],points[1])
	await frames(20)
	var route := await WalkTest._walk(scene,points.slice(1),label+"_out")
	check(label+"_out",route["pass"],route)
	if both and route["pass"]:
		points.reverse()
		var back := await WalkTest._walk(scene,points.slice(1),label+"_back")
		check(label+"_back",back["pass"],back)

func public_floor(xy: Array, start_height: float) -> Vector3:
	var start:=Vector3(xy[0],start_height+3.0,-xy[1])
	var ray:=PhysicsRayQueryParameters3D.create(start,start-Vector3.UP*32,1)
	var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.position+Vector3.UP*.045 if not hit.is_empty() else Vector3.INF

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	var graphics := DisplayServer.get_name() != "headless"
	if graphics: RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	current_scene=scene
	for n in 1400:
		if scene.get("gameplay"): break
		await physics_frame
	if not check("first_shift",scene.get("gameplay")!=null):
		quit(2)
		return
	await frames(24)
	if graphics: scene.hud.hide()
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var all_halls := "--all-halls" in OS.get_cmdline_user_args()
	if all_halls:
		for i in layout.plots.size():
			var plot: Dictionary=layout.plots[i]
			if plot.has("superseded_by"):
				continue
			var front: float=-plot.depth/2.0
			var door: float=plot.door_u
			var test := [world(plot,door,front-.94,.072),world(plot,door,front+.75,.072),
				world(plot,door,-front+.79,.072)]
			await trial("hall_%02d"%i,test,false)
			if plot.has("room"):
				var room: Dictionary=plot.room
				var visit := [world(plot,door,front-.94,.072),world(plot,door,room.door_v,.072),
					world(plot,room.inside_u,room.door_v,.072)]
				await trial("household_%02d"%i,visit)
		FileAccess.open(output.path_join("checks.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
		quit(2 if ever_failed else 0)
		return
	for p: Dictionary in layout.destinations:
		var site: String=SHORT[p.name]
		var f: float=p.front_offset
		var u: float=DOORS[site]
		if graphics:
			await shot(site+"_street",world(p,-8.4,f-6.1,1.43),world(p,u+1,f+.4,1.52))
			await shot(site+"_hall",world(p,u+.28,f+.73,1.64),world(p,u+2.05,-f-1.6,1.26))
			await shot(site+"_court",world(p,u+3,-f+3.55,1.64),world(p,u,-f-.2,1.45))
		else:
			var points := [world(p,u,f-1.96,.06),world(p,u,f+.95,.06),world(p,u,.05,.06),world(p,u,-f+.85,.06)]
			scene.explorer.begin_route_test(points[0],points[1])
			await frames(24)
			var result := await WalkTest._walk(scene,points.slice(1),site+"_through")
			check(site+"_through",result["pass"],result)
			if result["pass"]:
				points.reverse()
				var back := await WalkTest._walk(scene,points.slice(1),site+"_return")
				check(site+"_return",back["pass"],back)
	for p: Dictionary in layout.get("plots",[]):
		if graphics and p.has("room") and int(p.plot_id) in [3,4,5,7]:
			var r: Dictionary=p.room
			await shot("ordinary_%02d"%int(p.plot_id),world(p,r.jamb_u,r.door_v,1.63),
				world(p,r.inside_u,-p.depth/2.0+1.32,.89))
		if not p.has("court"): continue
		var c: Dictionary=p.court
		var named: bool=not String(p.name).is_empty()
		var label: String=SHORT[p.name] if named else "residence_%02d"%layout.plots.find(p)
		var h: float=c.upper_m
		var f: float=-p.depth/2
		var step_u: float=c.stair_u
		if graphics and named:
			await shot(label+"_yard",world(p,p.door_u,-f+.45,1.66),world(p,step_u*.35,c.landing_v+1.1,2.20))
			await shot(label+"_gallery",world(p,step_u,c.landing_v,h+1.64),world(p,c.room_u,c.room_v-.25,h+1.47))
			await shot(label+"_room",world(p,c.room_u,c.room_v,h+1.60),world(p,c.room_u+1.8,-f+12.7,h+.96))
			if c.has("bed_local"):
				await shot(label+"_bed",world(p,c.room_u,c.room_v,h+1.59),world(p,c.bed_local[0],c.bed_local[1],h+.57))
				await shot(label+"_counter",world(p,p.door_u-.24,f+.24,1.61),world(p,p.door_u+3.27,f+1.85,1.24))
		elif not graphics:
			var stops := [world(p,p.door_u,f-.93,.072),world(p,p.door_u,-f+.62,.13),
				world(p,step_u,-f+.62,.13),world(p,step_u,c.landing_v,h+.04),
				world(p,c.room_u,c.landing_v,h+.04),world(p,c.room_u,c.room_v,h+.04)]
			await trial(label+"_home",stops)
	if not graphics:
		var tested := {}
		for lane: Dictionary in layout.get("lanes",[]):
			if lane.type!="shared": continue
			var one: Dictionary=layout.plots[lane.plots[0]]
			var key:=str(signf(one.east_north[0]))+"_"+str(signf(one.east_north[1]))
			if tested.has(key): continue
			var two: Dictionary=layout.plots[lane.plots[1]]
			if one.has("superseded_by") or two.has("superseded_by"):
				continue
			var points: Array=[public_floor(lane.points[0],one.height), public_floor(lane.points[1],two.height)]
			if not points.has(Vector3.INF):
				await trial("shared_%s_%s"%[lane.plots[0],lane.plots[1]],points)
				tested[key]=true
	FileAccess.open(output.path_join("checks.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
