extends "res://../../scene_r24/day_one/verify.gd"

const SITE := "res://assets/district_500/zhongxing-bridge-18-21.json"
const DECK := "COL_R24_LinkDeck_R24_link_asphalt"

func world(point: Array) -> Vector3:
	return Vector3(point[0],point[2],-point[1])

func coords(p: Vector3) -> Array:
	return [p.x,-p.z,p.y]

func deck_hit(p: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.4,p-Vector3.UP*.45,1)
	query.hit_back_faces=false
	var hit := scene.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {}
	return {"name":str(hit.collider.get_parent().name),"height":hit.position.y,"normal_y":hit.normal.y}

func run_leg(points: Array, direction: String) -> Dictionary:
	var start := world(points.front())
	var facing := world(points[1])-start
	bike.global_position=start+Vector3.UP*.19
	bike.rotation=Vector3(0,atan2(-facing.x,-facing.z),0)
	bike.velocity=Vector3.ZERO
	bike.speed=0.0
	bike.parked=false
	bike.last_obstacle={}
	bike.test_throttle=0.
	bike.test_brake=true
	await frames(22)
	var established := bike.is_on_floor() and not bike.is_on_ceiling()
	var from: Vector3 = bike.global_position
	var last := from
	var run_metres := 0.0
	var next := 1
	var trace := [coords(from)]
	var airborne := 0
	var deck_contacts := 0
	for tick in 1000:
		var pos: Vector3 = bike.global_position
		var wanted := world(points[next])-pos
		wanted.y=0
		if wanted.length()<.66:
			next+=1
			if next==points.size():
				break
			wanted=world(points[next])-pos
			wanted.y=0
		var turn: float=(-bike.global_basis.z).signed_angle_to(wanted.normalized(),Vector3.UP)
		bike.test_steer=clampf(turn*2.45,-1.,1.)
		bike.test_brake=bike.speed>3.30
		bike.test_throttle=1.0 if bike.speed<2.95 else 0.0
		await physics_frame
		var p: Vector3 = bike.global_position
		run_metres+=last.distance_to(p)
		last=p
		airborne+=int(not bike.is_on_floor())
		if tick%12==0:
			trace.append(coords(p))
			deck_contacts+=int(deck_hit(p).get("name","")==DECK)
	bike.test_throttle=0.
	bike.test_brake=true
	await frames(31)
	trace.append(coords(bike.global_position))
	return {"direction":direction,"passed":established and next==points.size() and airborne==0 and deck_contacts>18,
		"reached":next-1,"targets":points.size()-1,"distance_m":run_metres,"airborne_ticks":airborne,
		"settled_start_on_deck":established,"deck_contact_samples":deck_contacts,"end_speed":bike.speed,
		"last_contact":bike.last_obstacle.duplicate(true),"trace":trace}

func verify() -> void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(12)
	game=scene.gameplay
	bike=game.scooter
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SITE))
	var points: Array=plan.upper_scooter_18.duplicate(true)
	var baseline := "--qa-without-zhongxing-18-21" in OS.get_cmdline_user_args()
	check("legacy_frame_18",(scene.find_child("COL_Outer500_Frame_18",true,false)!=null)==baseline)
	var surf := []
	for p: Array in points:
		surf.append(deck_hit(world(p)))
	check("retained_road_surface",baseline or surf.all(func(hit: Dictionary) -> bool: return hit.get("name","")==DECK and hit.get("normal_y",0.)>.97),surf)
	bike.enter(game.actor)
	bike.automation=true
	var forward := await run_leg(points,"forward")
	points.reverse()
	var reverse := await run_leg(points,"reverse_closed_test")
	check("upper_forward",forward.passed,forward)
	check("upper_reverse_closed_test",reverse.passed,reverse)
	FileAccess.open(output.path_join("road-18.json"),FileAccess.WRITE).store_string(JSON.stringify({"scene":scene.scene_file_path,
		"candidate":scene.scene_identity.district_500,"surface_samples":surf,"reverse_is_closed_qa":true,
		"attempts":[forward,reverse],"checks":checks},"  "))
	quit(2 if ever_failed else 0)
