extends CharacterBody3D
## Limited-speed arcade scooter. Physics body stays upright; wheels set visual pitch.
signal message(text: String)
var rider: Node3D
var visual: Node3D
var articulation: Node3D
var rider_collision: CollisionShape3D
var parked: bool = true
var speed: float = 0.0
var automation: bool = false
var test_throttle: float = 0.0
var test_steer: float = 0.0
var test_brake: bool = false
var safe_park_position: Vector3
var last_exit: Vector3
var last_obstacle: Dictionary = {}

func _ready() -> void:
	collision_layer = 4
	collision_mask = 3
	floor_snap_length = 0.65
	floor_max_angle = deg_to_rad(32)
	safe_margin = 0.008
	var shape: CollisionShape3D = CollisionShape3D.new()
	var wheelbase: CapsuleShape3D = CapsuleShape3D.new()
	wheelbase.radius = .28
	wheelbase.height = 1.5
	shape.shape = wheelbase
	shape.rotation.x = PI/2
	shape.position.y = .28
	add_child(shape)
	var upright: CollisionShape3D = CollisionShape3D.new()
	var body_box: BoxShape3D = BoxShape3D.new()
	body_box.size = Vector3(.74,.8,.80)
	upright.shape = body_box
	upright.position.y = .78
	add_child(upright)
	visual = Node3D.new()
	visual.name = "GroundedVisual"
	add_child(visual)
	articulation=preload("res://scripts/scooter_visual.gd").new()
	articulation.name="ArticulatedScooter"
	visual.add_child(articulation)
	rider_collision=CollisionShape3D.new()
	var torso: CapsuleShape3D=CapsuleShape3D.new()
	torso.radius=.22;torso.height=.76
	rider_collision.shape=torso;rider_collision.position=Vector3(0,1.34,.02)
	rider_collision.disabled=true;add_child(rider_collision)

func enter(actor: Node3D) -> bool:
	if is_instance_valid(rider) or absf(speed) > .15:
		return false
	rider = actor
	actor.can_control(false)
	actor.set_physics_process(false)
	actor.body.collision_layer = 0
	actor.body.collision_mask = 0
	actor.body.velocity = Vector3.ZERO
	parked = false
	articulation.set_occupied(true)
	rider_collision.set_deferred("disabled",false)
	safe_park_position = global_position
	message.emit("已上车 · W 前进 / S 刹车及倒车 · A D 转向 · 空格急刹 · P 停车 · E 下车")
	return true

func park() -> bool:
	if absf(speed) > .15 or not is_on_floor():
		message.emit("请先刹停，再按 P 停车")
		return false
	parked = true
	speed = 0.0
	safe_park_position = global_position
	message.emit("已停车 · E 安全下车，W 继续骑行")
	return true

func find_exit() -> Variant:
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = .31
	capsule.height = 1.75
	for offset in [Vector3(1.15,0,0),Vector3(-1.15,0,0),Vector3(0,0,1.65),Vector3(0,0,-1.65)]:
		var point: Vector3 = global_position + global_basis * offset
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(point+Vector3.UP*1.2, point-Vector3.UP*1.5,1)
		var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty() or hit.normal.y < .75:
			continue
		point = hit.position + Vector3.UP * .025
		var sweep: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(global_position+Vector3.UP,point+Vector3.UP,1)
		if not get_world_3d().direct_space_state.intersect_ray(sweep).is_empty():
			continue
		var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
		query.shape = capsule
		query.transform.origin = point + Vector3.UP * .875
		query.collision_mask = 1
		if get_world_3d().direct_space_state.intersect_shape(query,1).is_empty():
			return point
	return null

func exit_vehicle() -> bool:
	if not is_instance_valid(rider) or not parked or absf(speed) > .15:
		message.emit("请先刹停并按 P 停车")
		return false
	var point: Variant = find_exit()
	if point == null:
		message.emit("两侧空间不足，请换个位置停车")
		return false
	var actor: Node3D = rider
	rider = null
	articulation.set_occupied(false)
	rider_collision.set_deferred("disabled",true)
	last_exit = point
	actor.body.global_position = point
	# Publish the new position, then restore masks at the frame boundary. A
	# synchronous mask restore lets recovery see the rider's stale car-seat pose.
	actor.body.force_update_transform()
	actor.body.set_deferred("collision_layer",2)
	actor.body.set_deferred("collision_mask",5)
	actor.body.velocity = Vector3.ZERO
	actor.camera.global_position = point + Vector3.UP * 1.65
	actor.camera.look_at(global_position + Vector3.UP)
	actor._sync_angles()
	actor.set_physics_process(true)
	actor.can_control(true)
	message.emit("已下车 · 电瓶车留在停车位置")
	return true

func _physics_process(delta: float) -> void:
	var throttle: float = test_throttle if automation else (float(Input.is_physical_key_pressed(KEY_W))-float(Input.is_physical_key_pressed(KEY_S)))
	var steer: float = test_steer if automation else (float(Input.is_physical_key_pressed(KEY_A))-float(Input.is_physical_key_pressed(KEY_D)))
	var brake: bool = test_brake if automation else Input.is_physical_key_pressed(KEY_SPACE)
	if not is_instance_valid(rider):
		throttle = 0.0
		steer = 0.0
	if parked and is_instance_valid(rider) and throttle > 0.0:
		parked = false
	if parked or brake:
		speed = move_toward(speed,0.0,9.0*delta)
	elif throttle != 0.0:
		var acceleration: float = 7.0 if throttle * speed < 0.0 else 2.8
		speed = move_toward(speed,6.0 if throttle>0 else -1.8,acceleration*delta)
	else:
		speed = move_toward(speed,0.0,1.2*delta)
	var effective_steer: float=articulation.steer_angle/.32
	rotation.y += effective_steer * signf(speed) * minf(absf(speed)/2.0,1.0) * 1.15 * delta
	var forward: Vector3 = -global_basis.z
	velocity.x = forward.x * speed
	velocity.z = forward.z * speed
	velocity.y = -0.3 if is_on_floor() else velocity.y - 22.0*delta
	var before_move: Vector3=global_position
	move_and_slide()
	if is_on_wall():
		for index in range(get_slide_collision_count()):
			var hit: KinematicCollision3D = get_slide_collision(index)
			last_obstacle = {"body":str(hit.get_collider().get_parent().name),"normal":str(hit.get_normal()),"position":str(hit.get_position())}
		speed = 0.0
	if global_position.y < -10 or absf(global_position.x)>102 or absf(global_position.z)>102:
		global_position = safe_park_position
		velocity = Vector3.ZERO
		speed = 0.0
		parked = true
	_fit_wheels()
	var travel: float=(global_position-before_move).dot(forward)
	articulation.update_motion(delta,speed,steer,travel if absf(travel)<1.0 else 0.0)
	if is_instance_valid(rider):
		rider.body.global_position = global_position
		var focus: Vector3 = global_position + Vector3.UP * 1.2
		var desired: Vector3 = global_position + global_basis.z * 3.1 + Vector3.UP * 2.0
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(focus,desired,1)
		var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(ray)
		rider.camera.global_position = hit.position + hit.normal*.2 if not hit.is_empty() else desired
		rider.camera.look_at(focus + forward*.8)

func _fit_wheels() -> void:
	var heights: Array[float] = []
	for z in [.58,-.66]:
		var p: Vector3 = global_position + global_basis * Vector3(0,0,z)
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(p+Vector3.UP,p-Vector3.UP,1)
		var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty():
			return
		heights.append(hit.position.y)
	visual.rotation.x = atan2(heights[1]-heights[0],1.24)
	visual.position.y = (heights[0]+heights[1])*.5-global_position.y-.003
