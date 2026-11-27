extends SceneTree
## Drive the stock player scooter in the normal scene, with one placement per test direction.

var world: Node3D
var bike: CharacterBody3D
var rider: Node3D
var route: PackedVector2Array
var lengths: PackedFloat32Array
var output: String
var floor_nodes: PackedStringArray
var plan: Dictionary
var frames := {}

func _initialize() -> void:
	call_deferred("verify")

func enu(p: Vector3) -> Array:
	return [p.x,-p.z,p.y]

func direction(i: int) -> Vector2:
	return (route[i+1]-route[i]).normalized()

func prepare(points: Array) -> void:
	route.clear()
	lengths.clear()
	for point: Array in points:
		var p := Vector2(point[0],point[1])
		lengths.append(0.0 if route.is_empty() else lengths[-1]+p.distance_to(route[-1]))
		route.append(p)

func nearest(p: Vector2) -> Vector2:
	var distance := INF
	var along := 0.0
	for i in range(route.size()-1):
		var point := Geometry2D.get_closest_point_to_segment(p,route[i],route[i+1])
		var d := p.distance_to(point)
		if d<distance:
			distance=d
			along=lengths[i]+point.distance_to(route[i])
	return Vector2(along,distance)

func point_at(distance: float) -> Vector2:
	for i in range(route.size()-1):
		if distance<=lengths[i+1]:
			return route[i]+direction(i)*maxf(0.,distance-lengths[i])
	return route[-1]+direction(route.size()-2)*minf(2.,distance-lengths[-1])

func cast(a: Vector3,b: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a,b,1)
	var hit := world.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {}
	return {"name":str(hit.collider.get_parent().name),"enu":enu(hit.position),"normal":enu(hit.normal)}

func floor_at(point: Vector2,y: float,above: float,below: float) -> Dictionary:
	return cast(Vector3(point.x,y+above,-point.y),Vector3(point.x,y-below,-point.y))

func section(rows: Array) -> Dictionary:
	var samples := []
	var anchors := []
	var last := {}
	var max_measured_grade := 0.0
	var min_normal := 1.0
	var max_error := 0.0
	var misses := 0
	for i in range(rows.size()-1):
		var a: Array=rows[i]
		var b: Array=rows[i+1]
		var start := Vector2(a[0][0],a[0][1])
		var length := float(b[1])-float(a[1])
		var axis := (Vector2(b[0][0],b[0][1])-start).normalized()
		var left := Vector2(-axis.y,axis.x)
		var count := maxi(1,ceili(length/.45))
		for j in range(count if i<rows.size()-2 else count+1):
			var s := length*j/count
			var h := lerpf(a[2],b[2],s/length)
			for offset: float in [-.57,0.,.57]:
				var p := start+axis*s+left*offset
				var hit := floor_at(p,h,.42,.47)
				if hit.is_empty() or not hit.name in floor_nodes:
					misses+=1
					continue
				max_error=maxf(max_error,absf(hit.enu[2]-h))
				min_normal=minf(min_normal,hit.normal[2])
				var station := float(a[1])+s
				var item := {"s_m":station,"across_m":offset,"design_height_m":h,"floor":hit}
				samples.append(item)
				if offset==0.:
					if not last.is_empty():
						var span := station-float(last.s_m)
						if span>.18:
							var rise := float(hit.enu[2])-float(last.floor.enu[2])
							max_measured_grade=maxf(max_measured_grade,absf(rise)/span)
					last=item
				if station<.5 or float(rows[-1][1])-station<.5:
					anchors.append(item)
	return {"pass":misses==0 and min_normal>.975 and max_error<.09 and max_measured_grade<.165,
		"max_measured_grade":max_measured_grade,"min_floor_normal_up":min_normal,"max_height_error_m":max_error,
		"samples":samples,"misses":misses,"anchors":anchors}

func adjoining_lanes(controls: Dictionary) -> Dictionary:
	var samples := []
	var minimum := 8.
	var wrong := 0
	for lane: Dictionary in controls.lane_probes:
		var axis := Vector2(lane.direction[0],lane.direction[1]).normalized()
		var left := Vector2(-axis.y,axis.x)
		for row: Array in lane.centres:
			for offset: float in [-1.20,0.,1.20]:
				var en := Vector2(row[0],row[1])+left*offset
				var ground := floor_at(en,row[2],.24,.20)
				if ground.is_empty() or not ground.name in lane.surfaces:
					wrong+=1
					continue
				var p := Vector3(en.x,ground.enu[2],-en.y)
				var upper := cast(p+Vector3.UP*.1,p+Vector3.UP*8.)
				if not upper.is_empty():
					minimum=minf(minimum,upper.enu[2]-p.y)
				samples.append({"lane":lane.way,"offset_m":offset,"floor":ground,"overhead":upper})
	return {"pass":wrong==0 and minimum>2.10,"minimum_clearance_m_within_8m":null if minimum==8. else minimum,
		"misses":wrong,"samples":samples}

func sample_ground(z: float,y: float) -> Dictionary:
	var p := bike.global_position + bike.global_basis*Vector3(0,0,z)
	return floor_at(Vector2(p.x,-p.z),y,.9,1.65)

func driving_tick(progress: Vector2) -> void:
	var aim := point_at(progress.x + clampf(bike.speed*.65,1.1,3.2))
	var delta := aim-Vector2(bike.global_position.x,-bike.global_position.z)
	var target_yaw := atan2(-delta.x,delta.y)
	bike.test_steer=clampf(angle_difference(bike.rotation.y,target_yaw)*3.6,-1.,1.)

func capture(name: String) -> void:
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var image := root.get_texture().get_image()
	var result := image.save_png(output.path_join(name+".png"))
	frames[name]={"saved":result==OK,"size":[image.get_width(),image.get_height()],"rider_enu":enu(bike.global_position)}

func ride(points: Array,name: String,start_y: float,start_names: Array) -> Dictionary:
	prepare(points)
	var start := floor_at(route[0],start_y,.45,1.)
	if start.is_empty() or not start.name in start_names:
		return {"name":name,"pass":false,"reason":"start surface missing","hit":start}
	if bike.has_driver():
		bike.test_brake=true
		for i in range(45):
			await physics_frame
		if not (bike.park() and bike.exit_vehicle()):
			return {"name":name,"pass":false,"reason":"previous fixture could not dismount"}
		await physics_frame
	bike.automation=true
	bike.test_throttle=0.
	bike.test_steer=0.
	bike.test_brake=false
	bike.global_position=Vector3(route[0].x,start.enu[2]+.04,-route[0].y)
	var first := direction(0)
	bike.rotation=Vector3(0,atan2(-first.x,first.y),0.)
	bike.velocity=Vector3.ZERO
	bike.speed=0.
	bike.parked=true
	bike.last_obstacle={}
	for i in range(32):
		await physics_frame
	if not bike.enter(rider) or not bike.is_on_floor():
		return {"name":name,"pass":false,"reason":"scooter failed to settle or mount","hit":start}

	var brake_at := float(plan.brake_at_m) if name=="mapped_downhill" else lengths[-1]-.85
	var treatments := []
	var brake_tick := -1
	var brake_origin := Vector3.ZERO
	var brake_report := {}
	var brake_hold := Vector3.ZERO
	var brake_speed := 0.
	var run := []
	var recent := []
	var stage := "drive"
	var bad_frames := 0
	var max_lost := 0
	var airborne := 0
	var max_airborne := 0
	var lowest_up := 1.
	var max_deviation := 0.
	var travelled := 0.
	var max_step := 0.
	var peak_speed := 0.
	var min_clearance := 100.
	var support := {}
	var last := bike.global_position
	var reason := "timeout"
	var origin := last
	var farthest := 0.
	var stall := 0
	for tick in range(2100):
		var now := bike.global_position
		var xy := Vector2(now.x,-now.z)
		var progress := nearest(xy)
		var flat_step := Vector2(now.x-last.x,now.z-last.z).length()
		travelled+=flat_step
		max_step=maxf(max_step,flat_step)
		max_deviation=maxf(max_deviation,progress.y)
		peak_speed=maxf(peak_speed,bike.speed)
		last=now
		var under := floor_at(xy,now.y,.37,1.65)
		var supported: bool = bike.is_on_floor() and not under.is_empty() and under.name in floor_nodes
		bad_frames=0 if supported else bad_frames+1
		max_lost=maxi(max_lost,bad_frames)
		airborne=0 if bike.is_on_floor() else airborne+1
		max_airborne=maxi(max_airborne,airborne)
		if not under.is_empty():
			lowest_up=minf(lowest_up,under.normal[2])
			support[under.name]=int(support.get(under.name,0))+1
		if tick%8==0 or bad_frames==1:
			var roof := cast(now+Vector3.UP*.42,now+Vector3.UP*8.)
			if not roof.is_empty():
				min_clearance=minf(min_clearance,roof.enu[2]-now.y)
			var row := {"tick":tick,"enu":enu(now),"course_m":progress.x,"off_axis_m":progress.y,
				"speed_m_s":bike.speed,"on_floor":bike.is_on_floor(),"floor":under,
				"front":sample_ground(-.66,now.y),"rear":sample_ground(.58,now.y),"roof":roof,"stage":stage}
			run.append(row)
			recent.append(row)
			if recent.size()>10:
				recent.pop_front()
		if progress.x>farthest+.04:
			farthest=progress.x
			stall=0
		elif stage=="drive":
			stall+=1
		if bad_frames>12 or stall>135 or progress.y>1.8 or flat_step>1.2:
			reason="lost carriageway" if bad_frames>12 else ("stalled" if stall>135 else "left test line or recovered")
			break
		if stage=="drive" and brake_tick<0 and progress.x>=brake_at:
			brake_tick=tick
			brake_speed=bike.speed
			brake_origin=now
			stage="brake"
		elif stage=="brake" and absf(bike.speed)<.015:
			brake_hold=now
			brake_report={"speed_before_m_s":brake_speed,"time_s":(tick-brake_tick)/60.,
				"distance_m":now.distance_to(brake_origin),"stop_floor":under,"stopped_on_floor":bike.is_on_floor(),
				"position_enu":enu(now),"course_m":progress.x,"tick":tick}
			stage="hold"
		elif stage=="hold" and tick-int(brake_report.tick)>=60:
			brake_report["hold_drift_m"]=now.distance_to(brake_hold)
			treatments.append(brake_report.duplicate(true))
			if name=="mapped_downhill" and DisplayServer.get_name()!="headless":
				await capture("downhill-brake-stop")
			if name=="closed_uphill" or progress.x>=lengths[-1]-1.4:
				reason="completed"
				break
			stage="drive"
		if name=="mapped_downhill" and stage=="drive" and brake_tick>=0 and progress.x>=lengths[-1]-.85:
			reason="completed"
			break
		if name=="mapped_downhill" and progress.x >= lengths[-1]-8.6 and not frames.has("toward-jiefang-merge") and DisplayServer.get_name()!="headless":
			await capture("toward-jiefang-merge")
		bike.test_throttle=0. if stage!="drive" or bike.speed>4.25 else 1.
		bike.test_brake=stage!="drive"
		if stage=="drive":
			driving_tick(progress)
		await physics_frame
	bike.test_throttle=0.
	bike.test_brake=true
	var completed := reason=="completed" and farthest>=lengths[-1]-1.5
	var brakes_ok: bool = not treatments.is_empty() and treatments[0].stopped_on_floor and treatments[0].hold_drift_m<.14
	return {"name":name,"pass":completed and brakes_ok and max_lost<=6 and max_deviation<1.5 and min_clearance>1.80,
		"reason":reason,"distance_m":travelled,"route_m":lengths[-1],"farthest_m":farthest,
		"start":enu(origin),"end":enu(bike.global_position),"peak_speed_m_s":peak_speed,"max_off_axis_m":max_deviation,
		"max_step_m":max_step,"max_consecutive_unsupported_frames":max_lost,"min_floor_normal_up":lowest_up,
		"max_consecutive_airborne_frames":max_airborne,
		"min_overhead_clearance_within_8m":null if min_clearance==100. else min_clearance,
		"surfaces":support,"braking":treatments,"trace":run,"final_obstacle":bike.last_obstacle}

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	DirAccess.make_dir_recursive_absolute(output)
	var plan_path := OS.get_environment("CQ_RAMP_PLAN")
	if plan_path.is_empty():
		plan_path=get_script().resource_path.get_base_dir().path_join("grade-1256840008.json")
	var controls: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	plan=controls.ride
	floor_nodes=PackedStringArray(plan.surfaces)
	RenderingServer.render_loop_enabled=false
	world=load("res://first_shift.tscn").instantiate()
	root.add_child(world)
	current_scene=world
	for i in range(1400):
		if world.get("gameplay"):
			break
		await physics_frame
	for i in range(24):
		await physics_frame
	bike=world.gameplay.scooter
	rider=world.explorer
	if DisplayServer.get_name()!="headless":
		world.hud.hide()
	var down := await ride(plan.course,"mapped_downhill",plan.start_heights[0],plan.start_surfaces[0])
	var reverse: Array=plan.course.duplicate()
	reverse.reverse()
	var up := await ride(reverse,"closed_uphill",plan.start_heights[1],plan.start_surfaces[1])
	var baseline := OS.get_environment("CQ_RAMP_BASELINE")=="1"
	var evidence := {"engine":Engine.get_version_info().string,"scene":world.scene_file_path,
		"vehicle":str(bike.name),"controller":bike.get_script().resource_path,"Hz":Engine.physics_ticks_per_second,
		"baseline":baseline,"initial_placements_per_leg":1,
		"teleports_while_riding":0,"normal_one_way":"1256839997 → 1256840008 → 830761786",
		"reverse_test_closed":true,"rides":[down,up],"native_frames":frames}
	FileAccess.open(output.path_join("rider.json"),FileAccess.WRITE).store_string(JSON.stringify(evidence,"  "))
	for result: Dictionary in evidence.rides:
		print("CQ_RAMP_RIDE ",result.name," ",result.pass," ",result.reason)
	if baseline:
		quit(0 if down.pass and up.pass else 2)
		return
	var model: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/raijiapo-east-bend.json"))
	var ramp := section(model.road_sections_enu_m["1256840008"])
	var adjacent := adjoining_lanes(controls)
	var measurements := {"ramp":ramp,"adjacent":adjacent,"node":controls.node,"render_backend":"headless physics"}
	FileAccess.open(output.path_join("surface.json"),FileAccess.WRITE).store_string(JSON.stringify(measurements,"  "))
	print("CQ_RAMP_SURFACE ",ramp.pass," ",ramp.samples.size()," ",ramp.misses," grade ",ramp.max_measured_grade,
		" adjacent ",adjacent.pass," ",adjacent.samples.size()," ",adjacent.misses)
	quit(0 if down.pass and up.pass and ramp.pass and adjacent.pass else 2)
