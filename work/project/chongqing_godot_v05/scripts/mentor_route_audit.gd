extends Node
## Observe the real instructor from a separate physics callback. Never move either rider.
var issue_file := ""
var guide: CharacterBody3D
var lesson: Node3D
var issues: Array[Dictionary] = []
var legs: Dictionary = {}
var route_key := ""
var previous := Vector3.ZERO
var clock := 0.
var baseline := INF
var airborne := 0.
var last_contact := ""
var active_stall := -1
var airborne_reported := false
var elapsed := 0.
var peak_frame_step := 0.

func setup(controller: Node3D, file: String) -> void:
	issue_file = file
	lesson = controller
	guide = controller.mentor
	process_physics_priority = 10
	previous = guide.global_position

func stamp() -> Dictionary:
	return {"time_s":snappedf(elapsed,.01),"stage":lesson.Step.keys()[lesson.step],"segment":guide.next_point,"position":str(guide.global_position)}

func obstacle() -> String:
	var space := guide.get_world_3d().direct_space_state
	for height: float in [.22,.55,1.05]:
		var start := guide.global_position+Vector3.UP*height
		var query := PhysicsRayQueryParameters3D.create(start,start-guide.global_basis.z*1.9,guide.collision_mask)
		query.exclude = [guide.get_rid()]
		var hit := space.intersect_ray(query)
		if not hit.is_empty() and hit.normal.y < .76:
			var collider: Node = hit.collider
			return str(collider.get_path())
	return last_contact

func flag(kind: String, details: Dictionary) -> int:
	var event := stamp()
	event["kind"] = kind
	event.merge(details)
	issues.append(event)
	write_issues()
	print("PENG_ROUTE_ISSUE ",JSON.stringify(event))
	return issues.size()-1

func close_stall(reason: String) -> void:
	if active_stall >= 0:
		issues[active_stall]["ended_at_s"] = snappedf(elapsed,.01)
		issues[active_stall]["end_reason"] = reason
		active_stall = -1
		write_issues()
	clock = 0.
	baseline = INF
	last_contact = ""

func _physics_process(delta: float) -> void:
	elapsed += delta
	var point := guide.global_position
	var travel := point.distance_to(previous)
	previous = point
	var key: String = "%d/%s" % [lesson.round_index+1,lesson.Step.keys()[lesson.step]]
	var driving: bool = lesson.step in [lesson.Step.TO_SHOP,lesson.Step.TO_YARD] and not guide.path.is_empty()
	if lesson.step==lesson.Step.DONE and lesson.return_boarded and lesson.demo and lesson.demo.action==lesson.demo.Action.RIDING:
		driving=not guide.path.is_empty()
		key="dispatch/%d"%guide.trip_number
	if not driving:
		return
	if not legs.has(key):
		legs[key] = {"travel_m":0.,"moving_s":0.,"waiting_s":0.,"max_kmh":0.,"arrived":false,"waypoints":[]}
	var leg: Dictionary = legs[key]
	leg.travel_m += travel
	leg.max_kmh = maxf(leg.max_kmh,absf(guide.speed)*3.6)
	leg.arrived = guide.arrived or leg.arrived
	var segment_key := "%s/%d" % [key,guide.next_point]
	if segment_key != route_key:
		close_stall("changed_segment")
		route_key = segment_key
		leg.waypoints.append(stamp())
	peak_frame_step = maxf(peak_frame_step,travel)
	if travel > .85: flag("position_jump",{"distance_m":travel})
	if guide.escort and (guide.waiting or not is_instance_valid(guide.learner.rider)):
		leg.waiting_s += delta
		close_stall("learner_wait")
		return
	if guide.arrived:
		close_stall("arrived")
		return
	leg.moving_s += delta
	airborne = 0. if guide.is_on_floor() else airborne+delta
	if airborne > .45 and not airborne_reported:
		flag("wheelbase_off_ground",{"duration_s":airborne})
		airborne_reported = true
	if airborne == 0.: airborne_reported = false
	var goal: Vector3 = guide.path[guide.next_point]
	var remaining := Vector2(point.x-goal.x,point.z-goal.z).length()
	if remaining < 1.2:
		close_stall("approach")
		return
	for i in guide.get_slide_collision_count():
		var contact := guide.get_slide_collision(i)
		if contact.get_normal().y < .7 and contact.get_collider() is Node:
			last_contact = str(contact.get_collider().get_path())
	if remaining+.20 < baseline:
		close_stall("forward_progress")
		baseline = remaining
	clock += delta
	if clock > 3.0 and active_stall < 0:
		active_stall = flag("route_blocked",{"goal":str(goal),"obstacle":obstacle(),"seconds_without_progress":snappedf(clock,.01)})

func write_issues() -> void:
	if issue_file.is_empty(): return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(issue_file.get_base_dir()))
	var file := FileAccess.open(issue_file,FileAccess.WRITE)
	if file: file.store_string(JSON.stringify(report(),"\t"))

func report() -> Dictionary:
	return {"legs":legs,"issues":issues,"max_frame_displacement_m":peak_frame_step,"rules":{"stalled_seconds":3.0,"minimum_progress_m":.20,"airborne_seconds":.45}}
