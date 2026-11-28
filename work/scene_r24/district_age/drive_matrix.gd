extends "../../scene_r24/day_one/verify.gd"

const NanquGrade := preload("res://scripts/nanqu_rail_grade.gd")

const EAST_RAMP := &"COL_EastRoad_1256840008"
const EAST_RAMP_MERGE := &"COL_EastRoad_RampMerge_1865946191"

func ramp_start(point: Vector3, reverse: bool) -> Dictionary:
	# The historical samples belong to the lower road. At the reverse end
	# the ramp and the registered merge are just above that old surface.
	var window := Vector2(.004, .08) if reverse else Vector2(.34, .51)
	var ray := PhysicsRayQueryParameters3D.create(
		point + Vector3.UP * window.y, point + Vector3.UP * window.x, 1)
	ray.hit_back_faces = false
	var hit := scene.get_world_3d().direct_space_state.intersect_ray(ray)
	var collider: Node = hit.get("collider")
	# The imported trimesh body is a child of the named road node.
	var body_name := collider.get_parent().name if collider != null else &""
	var normal: Vector3 = hit.get("normal", Vector3.ZERO)
	var registered := body_name == EAST_RAMP or (reverse and body_name == EAST_RAMP_MERGE)
	return {
		"valid": registered and normal.y >= cos(bike.floor_max_angle),
		"historical_point": str(point),
		"vertical_window_m": [point.y + window.x, point.y + window.y],
		"body": body_name,
		"position": hit.get("position"),
		"normal": str(normal),
	}

func record_route(results: Array, result: Dictionary) -> void:
	results.append(result)
	print("ROUTE_MATRIX ", result.id, " ", result.state, " ", result.reached, "/", result.targets)
	FileAccess.open(output.path_join("drives.json"),FileAccess.WRITE).store_string(JSON.stringify(results))

func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"):await physics_frame
	await frames(12)
	game=scene.gameplay;lesson=game.lesson;bike=game.scooter
	var query:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/road_queries.json"))
	var grade_plan:=NanquGrade.installed_plan(scene)
	var lines:={}
	for row:Array in query.sections:
		if row[1]!=1 or row[4]==null:continue
		var id:=int(row[0])
		var p:=Vector3(row[2],row[4],row[3])
		if query.routes[id].name=="59146775": p.y+=NanquGrade.delta_at(p.x,grade_plan)
		if absf(p.x)>98.5 or absf(p.z)>98.5:continue
		if not lines.has(id):lines[id]=[]
		var pts:Array=lines[id]
		if pts.is_empty() or Vector2(pts[-1].x-p.x,pts[-1].z-p.z).length()>1.60:pts.append(p)
	var batch_id:=0
	var args := OS.get_cmdline_user_args()
	var reverse := "--reverse" in args
	for arg in args:
		if arg.begins_with("--batch="):batch_id=int(arg.trim_prefix("--batch="))
	var results:=[]
	var invalid_start := false
	bike.enter(game.actor);bike.automation=true
	for id:int in lines:
		if id%3!=batch_id:continue
		var pts:Array=lines[id].duplicate()
		if reverse:pts.reverse()
		if pts.size()<2:
			results.append({"id":id,"state":"outside_inner_test_area"});continue
		var result := {"id":id,"route":query.routes[id].name,"part":query.routes[id].part,
			"reached":0,"targets":pts.size()-1}
		var origin: Vector3 = pts[0]
		var spawn := {}
		if id == 12 and result.route == "1256840008" and result.part == 0 and scene.get("district_500_enabled"):
			spawn = ramp_start(origin, reverse)
			result["spawn_fixture"] = spawn
			if not spawn.valid:
				invalid_start = true
				result["state"] = "invalid_start_surface"
				record_route(results, result)
				continue
			origin = spawn.position
			spawn["position"] = str(origin)
		var d:Vector3=pts[1]-pts[0]
		# Only the initial spawn is placed. Every subsequent metre uses normal steering, throttle and collisions.
		bike.global_position=origin+Vector3.UP*.19;bike.rotation=Vector3(0,atan2(-d.x,-d.z),0)
		bike.velocity=Vector3.ZERO;bike.speed=0.;bike.parked=false;bike.last_obstacle={};bike.test_throttle=0.;bike.test_brake=true
		await frames(22)
		var start:Vector3=bike.global_position
		if not spawn.is_empty():
			spawn["settled_clearance_m"] = start.y - origin.y
			spawn["on_floor"] = bike.is_on_floor()
			spawn["on_ceiling"] = bike.is_on_ceiling()
			if not spawn.on_floor or spawn.on_ceiling or not (spawn.settled_clearance_m >= -.02 and spawn.settled_clearance_m <= .12):
				invalid_start = true
				result["state"] = "invalid_settled_start"
				record_route(results, result)
				continue
		var next:=1;var still:=0;var best:=INF;var history:Array=[];var tick:=0
		while tick<pts.size()*140+300 and next<pts.size() and still<210:
			var p:Vector3=bike.global_position
			var delta:Vector3=pts[next]-p;delta.y=0
			if delta.length()<.93:
				next+=1;still=0;best=INF;continue
			if delta.length()<best-.07:best=delta.length();still=0
			else:still+=1
			var steering:=(-bike.global_basis.z).signed_angle_to(delta.normalized(),Vector3.UP)
			bike.test_steer=clampf(steering*2.45,-1.,1.)
			var v:=2.0 if absf(steering)>.40 else 3.85
			bike.test_brake=bike.speed>v+.4
			bike.test_throttle=1. if bike.speed<v else 0.
			if tick%24==0:history.append([p.x,p.y,p.z,next])
			await physics_frame;tick+=1
		var pass_route:=next==pts.size()
		result.merge({"reached":next-1,"state":"passed" if pass_route else "stopped",
			"start":str(start),"end":str(bike.global_position),"goal":str(pts[mini(next,pts.size()-1)]),
			"last_contact":bike.last_obstacle.duplicate(true),"history":history}, true)
		record_route(results, result)
	quit(2 if invalid_start else 0)
