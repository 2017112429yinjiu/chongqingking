extends "../../../district_500/routes.gd"
## Reuse the stock player and scooter controls over the old wall line.
## Offsets are measured east of the same registered road centreline.

const SOUTH := Vector2(219.3073,143.6239)
const NORTH := Vector2(208.2481,216.1164)
const STATIONS := [167.0,170.0,173.0,176.1,178.3,181.0,184.0,187.0]

func ground_ray_top_m() -> float:
	return 66.0

func route_plan() -> Dictionary:
	var plan := {}
	for offset: float in [-3.75,-1.90,0.0,1.90,3.75]:
		var path := []
		for northing: float in STATIONS:
			var east := lerpf(SOUTH.x,NORTH.x,inverse_lerp(SOUTH.y,NORTH.y,northing))
			path.append([east+offset,northing])
		plan["zhongxing_east_offset_%+.2f_m" % offset] = path
	return plan

func leg(key: String, reverse: bool, riding: bool, route: Array) -> void:
	if not riding or not reverse or key != "zhongxing_east_offset_+1.90_m":
		await super.leg(key,reverse,riding,route)
		return
	var sequence := []
	var monitor := func():
		if Engine.get_physics_frames() % 12 != 0:
			return
		var place: Vector3 = bike.global_position
		if absf(place.z+176.6)>1.6 or not bike.has_driver():
			return
		var contacts := []
		for index in bike.get_slide_collision_count():
			var hit: KinematicCollision3D = bike.get_slide_collision(index)
			contacts.append({"body":str(hit.get_collider().get_parent().name),
				"xyz":str(hit.get_position()),"normal":str(hit.get_normal())})
		sequence.append({"bike_xyz":str(place),"speed":bike.speed,"wall":bike.is_on_wall(),"contacts":contacts})
	physics_frame.connect(monitor)
	await super.leg(key,reverse,riding,route)
	physics_frame.disconnect(monitor)
	FileAccess.open(output.path_join("crossing_wheel_contacts.json"),FileAccess.WRITE).store_string(
		JSON.stringify(sequence,"  "))
