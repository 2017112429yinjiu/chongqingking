class_name CQDistrictExplorer
extends Node3D
## Metre-scale scene inspection. Godot coordinates: Y up, north toward -Z.
## Walking and free-camera inspection controller; interactions live in main.gd.

signal mode_changed(walking: bool)
signal view_changed(name: String)

const EYE_HEIGHT: float = 1.65
const WALK_SPEED: float = 4.2
const RUN_SPEED: float = 7.5
const GRAVITY: float = 22.0
const JUMP_SPEED: float = 6.0
const STEP_HEIGHT: float = 0.45
const LOOK_SENSITIVITY: float = 0.0026

var camera: Camera3D
var body: CharacterBody3D
var walking: bool = false
var seated: bool = false
var _seated_eye: Vector3
var current_view: String = "overview"
var view_order: Array[String] = []
var _enabled: bool = true
var automation_driving: bool = false
var automation_axis: Vector2 = Vector2.ZERO
var _looking: bool = false
var body_view: Node3D
var body_gait: AnimationPlayer

func install_walking_body(model: PackedScene) -> void:
	body_view = model.instantiate() as Node3D
	body.add_child(body_view)
	body_view.visible = false
	body_gait = body_view.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if body_gait and not body_gait.get_animation_list().is_empty():
		var clip := body_gait.get_animation_list()[0]
		body_gait.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		body_gait.play(clip)
		body_gait.seek(.22, true)
		body_gait.speed_scale = 0.0

func _capture_view() -> void:
	if _enabled and DisplayServer.get_name() != "headless" and get_window().has_focus() and not _text_has_focus():
		_looking = true
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and _looking:
		_release_mouse()

var _jump_queued: bool = false
var _yaw: float = 0.0
var _pitch: float = -0.55
var _fly_multiplier: float = 1.0
var _walk_spawn: Vector3 = Vector3(15.0, 10.5, 76.0)
var _walk_target: Vector3 = Vector3(22.0, 18.0, 29.0)
var _last_walk_position: Vector3 = Vector3.ZERO
var _has_walk_position: bool = false
var _views: Dictionary = {
	"overview": {"position": Vector3(225.0, 225.0, 285.0), "target": Vector3(0.0, 22.0, 0.0)},
	"street": {"position": Vector3(15.0, 11.1, 76.0), "target": Vector3(22.0, 23.0, 29.0)},
	"residential": {"position": Vector3(61.0, 35.0, -77.0), "target": Vector3(20.0, 41.0, -65.0)}
}


func _ready() -> void:
	_ensure_nodes()
	go_to_view("overview")


func setup(spawn_points: Dictionary) -> void:
	_views.clear()
	for view_name in spawn_points.keys():
		if spawn_points.has(view_name) and spawn_points[view_name] is Dictionary:
			var info: Dictionary = spawn_points[view_name]
			if info.get("position") is Vector3 and info.get("target") is Vector3:
				_views[view_name] = info.duplicate()
	if spawn_points.get("walk_spawn") is Vector3:
		_walk_spawn = spawn_points["walk_spawn"]
	if spawn_points.get("walk_target") is Vector3:
		_walk_target = spawn_points["walk_target"]
	view_order.clear()
	for view_name in spawn_points.keys():
		if _views.has(view_name) and not str(view_name).begins_with("walk_"):
			view_order.append(str(view_name))
	if not view_order.is_empty():
		var first_view: String = view_order[0]
		if not _views.has("overview"):
			_views["overview"] = _views[first_view]
	_has_walk_position = false
	if is_inside_tree():
		_ensure_nodes()
		go_to_view("overview")


func _ensure_nodes() -> void:
	if is_instance_valid(camera):
		return
	body = CharacterBody3D.new()
	body.name = "WalkBody"
	body.collision_layer = 0
	body.collision_mask = 0
	body.floor_max_angle = deg_to_rad(58.0)
	body.floor_snap_length = 0.5
	body.floor_stop_on_slope = true
	body.safe_margin = 0.015
	body.max_slides = 6
	add_child(body)
	var shape_node: CollisionShape3D = CollisionShape3D.new()
	shape_node.name = "StandingCapsule"
	var shape: CapsuleShape3D = CapsuleShape3D.new()
	shape.radius = 0.30
	shape.height = 1.75
	shape_node.shape = shape
	shape_node.position = Vector3(0.0, 0.875, 0.0)
	body.add_child(shape_node)
	camera = Camera3D.new()
	camera.name = "ExplorerCamera"
	camera.near = 0.08
	camera.far = 1500.0
	camera.fov = 68.0
	add_child(camera)
	camera.current = true


func can_control(value: bool) -> void:
	_enabled = value
	if is_instance_valid(body_view):
		body_view.visible = value and walking and not seated
	if value:
		_capture_view()
	if not value:
		_jump_queued = false
		_release_mouse()
		if is_instance_valid(body):
			body.velocity.x = 0.0
			body.velocity.z = 0.0


func set_mode(value: bool) -> void:
	_ensure_nodes()
	if walking == value:
		return
	stand_up()
	_release_mouse()
	_jump_queued = false
	if value:
		walking = true
		body.collision_layer = 2
		body.collision_mask = 5
		body.velocity = Vector3.ZERO
		var from_street := not _has_walk_position and current_view.begins_with("r23_")
		var foot := _last_walk_position if _has_walk_position else _walk_spawn
		if from_street:
			var start := camera.global_position
			var ground := get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,start-Vector3.UP*3.2,1))
			if not ground.is_empty() and ground.normal.y>.7:foot=ground.position+Vector3.UP*.03
			else:from_street=false
		body.global_position = foot
		camera.global_position = foot + Vector3.UP * EYE_HEIGHT
		if not from_street:camera.look_at(_walk_target, Vector3.UP)
		_sync_angles()
		camera.fov = 68.0
		current_view = "walk"
		_capture_view()
	else:
		_last_walk_position = body.global_position
		_has_walk_position = true
		walking = false
		body.velocity = Vector3.ZERO
		body.collision_layer = 0
		body.collision_mask = 0
		current_view = "free"
	if is_instance_valid(body_view):
		body_view.visible = walking and _enabled
	mode_changed.emit(walking)
	view_changed.emit(current_view)


func go_to_view(view_name: String) -> void:
	_ensure_nodes()
	var key: String = view_name
	if key in ["aerial", "all", "top", "bird"]:
		key = "overview"
	if key == "walk":
		set_mode(true)
		_reset_walk()
		return
	if not _views.has(key):
		key = "overview"
	if walking:
		set_mode(false)
	_release_mouse()
	var info: Dictionary = _views[key]
	camera.fov = float(info.get("fov", 64.0))
	camera.global_position = info["position"]
	camera.look_at(info["target"], Vector3.UP)
	_sync_angles()
	current_view = key
	view_changed.emit(current_view)


func get_status() -> Dictionary:
	var pos: Vector3 = camera.global_position if is_instance_valid(camera) else Vector3.ZERO
	return {
		"walking": walking,
		"is_walking": walking,
		"mode": "walk" if walking else "fly",
		"mode_label": "步行查看" if walking else "自由观察",
		"view": current_view,
		"position": pos,
		"position_text": "东 %.1f m  北 %.1f m  高 %.1f m" % [pos.x, -pos.z, pos.y],
		"on_floor": body.is_on_floor() if is_instance_valid(body) else false,
		"mouse_captured": Input.mouse_mode == Input.MOUSE_MODE_CAPTURED,
		"enabled": _enabled
	}


func _sync_angles() -> void:
	_yaw = camera.global_rotation.y
	_pitch = clampf(camera.global_rotation.x, -1.48, 1.48)


func _release_mouse() -> void:
	_looking = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _text_has_focus() -> bool:
	var focus: Control = get_viewport().gui_get_focus_owner()
	return focus is LineEdit or focus is TextEdit


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
		_release_mouse()
		get_viewport().set_input_as_handled()
		return
	if not _enabled or _text_has_focus():
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			_capture_view()
			get_viewport().set_input_as_handled()
		elif event.pressed and not walking and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			var direction: float = -1.0 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0
			var amount: float = 9.0 if current_view == "overview" else 3.0
			camera.global_position += camera.global_basis.z * amount * direction
			get_viewport().set_input_as_handled()
	elif event is InputEventMouseMotion and _looking:
		_yaw -= event.relative.x * LOOK_SENSITIVITY
		_pitch = clampf(_pitch - event.relative.y * LOOK_SENSITIVITY, -1.48, 1.48)
		camera.global_rotation = Vector3(_pitch, _yaw, 0.0)
		get_viewport().set_input_as_handled()
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_TAB:
				set_mode(not walking)
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0:
				var index: int = 9 if event.physical_keycode == KEY_0 else event.physical_keycode - KEY_1
				if index < view_order.size():
					go_to_view(view_order[index])
			KEY_BRACKETLEFT:
				cycle_view(-1)
			KEY_BRACKETRIGHT:
				cycle_view(1)
			KEY_F:
				go_to_view("overview")
			KEY_R:
				if walking:
					_reset_walk()
				else:
					go_to_view(current_view if _views.has(current_view) else "overview")
			KEY_SPACE:
				if walking:
					_jump_queued = true


func _movement_axis() -> Vector2:
	if automation_driving:
		return automation_axis
	var direction: Vector2 = Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_W): direction.y -= 1.0
	if Input.is_physical_key_pressed(KEY_S): direction.y += 1.0
	if Input.is_physical_key_pressed(KEY_A): direction.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D): direction.x += 1.0
	return direction.normalized()


func _physics_process(delta: float) -> void:
	if not is_instance_valid(camera):
		return
	if seated:
		_jump_queued = false
		camera.global_position=camera.global_position.lerp(_seated_eye,1.0-exp(-9.0*delta))
		return
	var active: bool = _enabled and not _text_has_focus()
	var input_axis: Vector2 = _movement_axis() if active else Vector2.ZERO
	if walking:
		_move_walking(delta, input_axis, active)
	elif active:
		var move: Vector3 = camera.global_basis.x * input_axis.x + camera.global_basis.z * input_axis.y
		if Input.is_physical_key_pressed(KEY_E): move += Vector3.UP
		if Input.is_physical_key_pressed(KEY_Q): move -= Vector3.UP
		if move.length_squared() > 0.0:
			move = move.normalized()
		var speed: float = 30.0 if current_view == "overview" else 10.0
		if Input.is_physical_key_pressed(KEY_SHIFT): speed *= 2.5
		camera.global_position += move * speed * _fly_multiplier * delta


func _move_walking(delta: float, input_axis: Vector2, active: bool) -> void:
	var grounded: bool = body.is_on_floor()
	var basis: Basis = Basis(Vector3.UP, _yaw)
	var direction: Vector3 = basis.x * input_axis.x + basis.z * input_axis.y
	var speed: float = RUN_SPEED if active and Input.is_physical_key_pressed(KEY_SHIFT) else WALK_SPEED
	var accel: float = 25.0 if grounded else 9.0
	body.velocity.x = move_toward(body.velocity.x, direction.x * speed, accel * delta)
	body.velocity.z = move_toward(body.velocity.z, direction.z * speed, accel * delta)
	if not grounded:
		body.velocity.y -= GRAVITY * delta
	elif body.velocity.y < 0.0:
		body.velocity.y = 0.0
	if active and _jump_queued and grounded:
		body.velocity.y = JUMP_SPEED
	_jump_queued = false
	var stepped: bool = false
	if grounded and body.velocity.y <= 0.0:
		stepped = _try_step_up(Vector3(body.velocity.x, 0.0, body.velocity.z) * delta)
	var requested_velocity: Vector3 = body.velocity
	if stepped:
		# The swept step already performed this frame's horizontal movement.
		# A small downward motion refreshes the floor state at the actual landing.
		body.velocity = Vector3(0.0, -0.1, 0.0)
	body.move_and_slide()
	if stepped:
		body.velocity.x = requested_velocity.x
		body.velocity.z = requested_velocity.z
	if grounded and not body.is_on_floor() and body.velocity.y <= 0.0:
		body.apply_floor_snap()
	if body.global_position.y < -20.0 or absf(body.global_position.x) > 115.0 or absf(body.global_position.z) > 115.0:
		_reset_walk()
	camera.global_position = body.global_position + Vector3.UP * EYE_HEIGHT - basis.z * .14
	camera.global_rotation = Vector3(_pitch, _yaw, 0.0)
	if is_instance_valid(body_view):
		body_view.visible = walking and _enabled and not seated
		body_view.rotation.y = _yaw + PI
		if body_gait:
			var motion_speed := Vector2(body.velocity.x, body.velocity.z).length()
			body_gait.speed_scale = clampf(motion_speed / 1.6, 0.0, 2.4)


func _try_step_up(horizontal_motion: Vector3) -> bool:
	if horizontal_motion.length_squared() < 0.000001:
		return false
	var front_hit: KinematicCollision3D = KinematicCollision3D.new()
	# A capsule pressed against a short mesh edge may have its velocity reduced
	# to zero by move_and_slide. Probe a small, fixed distance ahead as well as
	# this frame's accelerated motion, so the recovery margin cannot prevent
	# the controller from discovering a valid low step at that edge.
	var front_probe: Vector3 = horizontal_motion.normalized() * maxf(horizontal_motion.length(), 0.08)
	if not body.test_move(body.global_transform, front_probe, front_hit, body.safe_margin, false, 4):
		return false
	# Sloped floors already work through move_and_slide; step only over steep faces.
	var found_steep_face: bool = false
	for index in range(front_hit.get_collision_count()):
		if front_hit.get_normal(index).dot(Vector3.UP) <= 0.65:
			found_steep_face = true
	if not found_steep_face:
		return false
	var raised: Transform3D = body.global_transform
	if body.test_move(raised, Vector3.UP * STEP_HEIGHT, null, body.safe_margin):
		return false
	raised.origin.y += STEP_HEIGHT
	# Check the shortest supported landing first. Advancing the swept capsule
	# to that landing matters: lifting only its Y position leaves it outside a
	# thin crossing path, so floor snapping pulls it back down on every frame.
	for distance in [horizontal_motion.length(), 0.14, 0.22, 0.30, 0.35]:
		var landing_motion: Vector3 = horizontal_motion.normalized() * maxf(horizontal_motion.length(), float(distance))
		if body.test_move(raised, landing_motion, null, body.safe_margin):
			continue
		var landing: Transform3D = raised
		landing.origin += landing_motion
		var down_hit: KinematicCollision3D = KinematicCollision3D.new()
		if not body.test_move(landing, Vector3.DOWN * (STEP_HEIGHT + 0.08), down_hit, body.safe_margin):
			continue
		if down_hit.get_normal().dot(Vector3.UP) < cos(body.floor_max_angle):
			continue
		var rise: float = STEP_HEIGHT + down_hit.get_travel().y
		if rise > 0.015 and rise <= STEP_HEIGHT + 0.01:
			body.global_position = landing.origin + down_hit.get_travel() + Vector3.UP * 0.008
			return true
	return false


func _reset_walk() -> void:
	stand_up()
	body.global_position = _walk_spawn
	body.velocity = Vector3.ZERO
	_last_walk_position = _walk_spawn
	_has_walk_position = false
	camera.global_position = body.global_position + Vector3.UP * EYE_HEIGHT
	camera.look_at(_walk_target, Vector3.UP)
	_sync_angles()
	_jump_queued = false

func sit_at(seat: Vector3, front: Vector3) -> void:
	if not walking:
		return
	body.velocity = Vector3.ZERO
	_seated_eye = seat + Vector3.UP*.83
	seated = true
	if is_instance_valid(body_view):body_view.visible = false
	var outward := Vector3(front.x-seat.x,0.,front.z-seat.z).normalized()
	camera.look_at(camera.global_position+outward-Vector3.UP*.085,Vector3.UP)
	_sync_angles()

func stand_up() -> void:
	if seated:
		seated=false
		camera.global_position=body.global_position+Vector3.UP*EYE_HEIGHT
		_jump_queued=false


func _exit_tree() -> void:
	_release_mouse()


## Deterministic controller input used by the included physics verification.
func begin_route_test(foot: Vector3, target: Vector3) -> void:
	set_mode(true)
	body.global_position = foot
	body.velocity = Vector3.ZERO
	camera.global_position = foot + Vector3.UP * EYE_HEIGHT
	aim_route_test(target)
	automation_axis = Vector2.ZERO
	automation_driving = true


## Steer a continuous verification walk without teleporting at route corners.
func aim_route_test(target: Vector3) -> void:
	var horizontal_target: Vector3 = Vector3(target.x, camera.global_position.y, target.z)
	if camera.global_position.distance_squared_to(horizontal_target) > 0.0001:
		camera.look_at(horizontal_target, Vector3.UP)
		_sync_angles()


func end_route_test() -> void:
	automation_axis = Vector2.ZERO
	automation_driving = false
	body.velocity = Vector3.ZERO


func cycle_view(direction: int) -> void:
	if view_order.is_empty():
		return
	var index: int = view_order.find(current_view)
	index = posmod(index + direction, view_order.size())
	go_to_view(view_order[index])
