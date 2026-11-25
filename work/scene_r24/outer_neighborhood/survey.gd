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
	FileAccess.open(output.path_join("checks.json"),FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	quit(2 if ever_failed else 0)
