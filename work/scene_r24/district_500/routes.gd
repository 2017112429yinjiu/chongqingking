extends SceneTree

# East/north coordinates. The start and finish of each leg are placed on a
# sampled road. Between placement and arrival the player's stock controller
# supplies every metre of movement.
const ROUTES := {
	"west": [[-91.,-74.87],[-100.,-72.442],[-114.71,-68.48],[-138.28,-61.63],[-156.39,-54.56],[-176.6,-45.19],[-192.93,-34.94],[-212.,-19.4]],
	"east": [[94.,-48.75],[100.,-43.717],[105.48,-39.11],[119.85,-27.43],[153.74,-.42],[182.4,21.73],[198.26,38.56],[205.08,48.08],[219.71,83.56]],
	"east_high": [[92.,87.20],[100.,90.621],[120.,99.15],[136.19,106.0],[145.16,109.75],[158.29,96.17],[165.70,88.02],[170.25,85.70],[180.51,87.13]],
	"north": [[-30.3,93.3],[-34.989,100.],[-45.04,114.38],[-55.95,135.83],[-48.,150.],[-37.,145.],[-12.,149.],[37.,160.]],
	"south": [[16.,-95.5],[16.,-102.],[16.,-111.],[18.,-130.],[23.,-153.],[60.,-137.],[105.,-124.]],
}
var scene: Node3D
var actor: Node3D
var bike: CharacterBody3D
var output: String
var records: Array = []
var space: PhysicsDirectSpaceState3D
var capture_native := false

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	output = OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	capture_native = DisplayServer.get_name() != "headless"
	if capture_native:
		RenderingServer.render_loop_enabled = false
	scene = load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for frame in range(900):
		await physics_frame
		if scene.get("gameplay"):
			break
	if not scene.get("gameplay"):
		quit(2)
		return
	await physics_frame
	if capture_native and "--software-capture" in OS.get_cmdline_user_args():
		for fixture: Light3D in scene.find_children("*", "Light3D", true, false):
			fixture.shadow_enabled = false
		root.use_occlusion_culling = false
	actor = scene.gameplay.actor
	bike = scene.gameplay.scooter
	space = scene.get_world_3d().direct_space_state
	var only := OS.get_environment("CQ_ROUTE")
	var plan := route_plan()
	for key: String in plan:
		if not only.is_empty() and key != only:
			continue
		for reverse: bool in [false,true]:
			for riding: bool in [false,true]:
				await leg(key,reverse,riding,plan[key])
	var failed := records.any(func(item: Dictionary) -> bool: return not item.passed)
	quit(1 if failed or records.is_empty() else 0)

func route_plan() -> Dictionary:
	return ROUTES

func leg(key: String, reverse: bool, riding: bool, route: Array) -> void:
	var coordinates := route.duplicate()
	if reverse:
		coordinates.reverse()
	var points: Array[Vector3] = []
	for value: Array in coordinates:
		points.append(Vector3(value[0],0,-value[1]))
	var start := points[0]
	var query := PhysicsRayQueryParameters3D.create(start+Vector3.UP*50,start-Vector3.UP*21,1)
	var contact := space.intersect_ray(query)
	if not contact.is_empty():
		start.y = contact.position.y + .045
	# Park the bike away when the walking test uses the same lane.
	bike.global_position = Vector3(55,28,-45)
	bike.safe_park_position = bike.global_position
	bike.velocity = Vector3.ZERO
	bike.speed = 0
	bike.parked = true
	bike.automation = true
	bike.test_brake = true
	bike.test_throttle = 0
	bike.last_obstacle = {}
	if bike.has_driver():
		bike.rider = null
		actor.set_mode(true)
	var facing := points[1]-points[0]
	actor.begin_route_test(start, start+facing)
	var entered := true
	if riding:
		bike.global_position = start
		bike.rotation = Vector3(0,atan2(-facing.x,-facing.z),0)
		entered = bike.enter(actor)
		for frame in range(12):
			await physics_frame
	var previous := start
	var travelled := 0.0
	var max_step := 0.0
	var samples: Array = []
	var best := INF
	var target := 1
	var frame := 0
	var still := 0
	var passed := false
	var native_frames := 0
	while entered and target < points.size() and frame < 8400 and still < 240:
		var actual: Vector3 = bike.global_position if riding else actor.body.global_position
		var delta := points[target]-actual
		delta.y = 0
		var d := delta.length()
		if d<(.86 if riding else .52):
			target += 1
			best = INF
			still = 0
			continue
		if d<best-.06:
			best=d
			still=0
		else:
			still+=1
		var motion := actual.distance_to(previous)
		max_step=maxf(max_step,motion)
		travelled+=motion
		previous=actual
		if riding:
			var steer := (-bike.global_basis.z).signed_angle_to(delta.normalized(),Vector3.UP)
			var speed := 2.15 if absf(steer)>.32 or d<3.0 else 4.5
			bike.test_steer=clampf(steer*2.5,-1.,1.)
			bike.test_brake=bike.speed>speed+.38
			bike.test_throttle=1. if bike.speed<speed else 0.
		else:
			actor.aim_route_test(actual+delta)
			actor.automation_axis=Vector2(0,-1)
		if frame%30==0:
			samples.append([actual.x,actual.y,actual.z,target])
		if capture_native and key=="east_high" and riding and not reverse and frame%9==0 and native_frames<28:
			RenderingServer.force_draw(false,1.0/60.0)
			root.get_texture().get_image().save_png(output.path_join("ride_%03d.png" % native_frames))
			native_frames+=1
		await physics_frame
		frame+=1
	var parked := true
	var exited := true
	if riding and entered:
		bike.test_throttle=0
		bike.test_brake=true
		for tick in range(65):
			await physics_frame
		parked=bike.park()
		exited=bike.exit_vehicle()
	if not riding:
		actor.end_route_test()
	passed=not contact.is_empty() and entered and target==points.size() and max_step<.65 and parked and exited
	var actual: Vector3=bike.global_position if riding else actor.body.global_position
	records.append({"route":key,"reverse":reverse,"riding":riding,"passed":passed,
		"mounted":entered if riding else null,"parked":parked if riding else null,"dismounted":exited if riding else null,
		"reached":target-1,"targets":points.size()-1,"distance_m":travelled,"max_tick_displacement_m":max_step,
		"stop":[actual.x,actual.y,actual.z],"contact":bike.last_obstacle if riding else {},
		"samples":samples,"native_frames":native_frames})
	FileAccess.open(output.path_join("routes.json"),FileAccess.WRITE).store_string(JSON.stringify({
		"engine":Engine.get_version_info().string,"renderer":RenderingServer.get_current_rendering_method(),"candidate":scene.scene_identity.get("district_500",{}),
		"routes":records},"  "))
	print("DISTRICT500_LEG ",key," ",reverse," ",riding," ",passed," targets ",target-1,"/",points.size()-1)
