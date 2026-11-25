extends SceneTree

const SURVEY := {
	"west_upper": [-100.0, -72.442], "west_lower": [-100.0, -80.232],
	"east_main": [100.0, -43.717], "east_high": [100.0, 90.621],
	"north": [-34.989, 100.0], "south": [16.0, -100.0],
	"southeast": [100.0, -98.476],
}
var scene: Node3D

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var graphics := DisplayServer.get_name() != "headless"
	if graphics:
		RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	if "--baseline" in OS.get_cmdline_user_args() and "district_500_enabled" in scene:
		scene.set("district_500_enabled", false)
	root.add_child(scene)
	for tick in range(900):
		await physics_frame
		if scene.get("gameplay"):
			break
	if not scene.get("gameplay"):
		quit(2)
		return
	for tick in range(20):
		await physics_frame
	var output := OS.get_environment("CQ_QA_DIR")
	if graphics:
		scene.hud.hide()
	DirAccess.make_dir_recursive_absolute(output)
	var space = scene.get_world_3d().direct_space_state
	var results := {}
	for key: String in SURVEY:
		var coords: Array = SURVEY[key]
		var origin := Vector2(coords[0], -coords[1])
		var outward := Vector2(signf(origin.x), 0) if absf(origin.x) == 100 else Vector2(0, signf(origin.y))
		var along := Vector2(-outward.y, outward.x)
		var points := []
		for across in range(-12,13):
			for depth: float in [-8.0,-4.0,-2.0,-1.0,-.4,-.04,.04,.4,1.0,2.0,4.0,8.0,16.0]:
				var p := origin+outward*depth+along*across*.5
				var hit := ground(space,p,9.35 if key=="south" else 53.0)
				points.append([across*.5,depth,p.x,p.y,hit[0],hit[1]])
		results[key] = points
	var outer := {}
	for entry in [["W",-249.,71.],["E",249.,40.],["N",48.,-249.],["S",145.,249.]]:
		outer[entry[0]] = ground(space,Vector2(entry[1],entry[2]))
	FileAccess.open(output.path_join("sections.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"sections":results,"outer":outer,"scene":scene.scene_file_path,"engine":Engine.get_version_info().string,
		"renderer":RenderingServer.get_current_rendering_method(),"shadows_disabled":"--software-capture" in OS.get_cmdline_user_args(),
		"candidate":scene.scene_identity.get("district_500",{}),"collision_stats":scene.get("collision_stats")}, "  "))
	if graphics:
		if "--software-capture" in OS.get_cmdline_user_args():
			for fixture: Light3D in scene.find_children("*", "Light3D", true, false):
				fixture.shadow_enabled=false
			scene.get_viewport().use_occlusion_culling = false
		await capture(output,"core",Vector3(-26.5,13.2,77),Vector3(-38,15.2,54),60)
		if "--baseline" not in OS.get_cmdline_user_args():
			await capture(output,"overview",Vector3(303,332,392),Vector3(0,15,0),64)
			var market_eye := Vector2(174,-104)
			var market_floor: Variant = ground(space,market_eye)[0]
			if market_floor != null:
				await capture(output,"east_market",Vector3(market_eye.x,market_floor+1.65,market_eye.y),Vector3(166,38.9,-115),66)
			for key: String in ["west_upper","east_main","east_high","north","south"]:
				var row: Array = SURVEY[key]
				var p := Vector2(row[0],-row[1])
				var outward := Vector2(signf(p.x),0) if absf(p.x)==100 else Vector2(0,signf(p.y))
				for direction: float in [-1.0,1.0]:
					var q := p+outward*direction*6
					var ceiling:=9.35 if key=="south" else 53.0
					var h: Variant = ground(space,q,ceiling)[0]
					if h == null:
						continue
					var center: Variant = ground(space,p,ceiling)[0]
					if center == null:
						center = h
					var start := Vector3(q.x,h+.45,q.y)
					await capture(output,key+("_back" if direction>0 else "_out"),start,Vector3(p.x,center+.57,p.y),70)
	quit()

func ground(space: PhysicsDirectSpaceState3D,p: Vector2,ceiling: float=53.0) -> Array:
	var q := PhysicsRayQueryParameters3D.create(Vector3(p.x,ceiling,p.y),Vector3(p.x,-22,p.y),1)
	var floor := space.intersect_ray(q)
	if floor.is_empty():
		return [null,""]
	return [floor.position.y,str(floor.collider.get_parent().name)]

func capture(output: String,label: String,position: Vector3,target: Vector3,fov: float) -> void:
	var camera := Camera3D.new()
	scene.add_child(camera)
	camera.position=position
	camera.look_at(target)
	camera.fov=fov
	camera.far=1400
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var image := root.get_texture().get_image()
	var result := image.save_png(output.path_join(label+".png"))
	print("DISTRICT500_IMAGE ",label," ",image.get_size()," ",result)
	camera.queue_free()
