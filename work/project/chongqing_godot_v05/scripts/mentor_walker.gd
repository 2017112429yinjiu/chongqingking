extends CharacterBody3D
## One rider mesh and skeleton move between the saddle and this walking capsule.
const FOOT_FRAME := Transform3D(Basis(Vector3.UP,PI),Vector3(0,-.055,.155))
const WALKER = preload("res://assets/block_r23/commuter.glb")
const WAIT = preload("res://assets/courtyard_r24/wait_clips.res")
var bike: CharacterBody3D
var human: Node3D
var animator: AnimationPlayer
var skeleton: Skeleton3D
var palms: Array[Vector3] = [Vector3.ZERO,Vector3.ZERO]
var offsets: Array[Vector3] = [Vector3.ZERO,Vector3.ZERO]
var hands: Array[int] = []
var digits: Array = [[],[]]
var hand_pose := preload("res://scripts/mentor_hands.gd").new()
var load_blend := 0.
var carrying := false
var grip_span := Vector3.FORWARD
var finger_bend := 0.
var carry_start := Vector3.ZERO
var arms:Array = []
var joints_world := {}
var inspect_joints:=false
var gaze := preload("res://scripts/mentor_gaze.gd").new()
var torso := preload("res://scripts/mentor_reach.gd").new()
var foot_shape := CollisionShape3D.new()
var transfer: Tween
var mounted := true
var path := PackedVector3Array()
var index := 0
var stop_radius := .14
var travelled := 0.
var blocked_s := 0.
var blocked_reported := false
var release_time := 0.
var released_torso := 0.

func setup(vehicle: CharacterBody3D) -> void:
	inspect_joints="--day-one-test" in OS.get_cmdline_user_args()
	bike = vehicle
	human = bike.articulation.human
	animator = bike.articulation.animator
	skeleton = human.find_children("*","Skeleton3D",true,false)[0]
	var source := WALKER.instantiate()
	var gait := source.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var library := AnimationLibrary.new()
	library.add_animation("walk",_retarget(gait.get_animation("street_walk")))
	library.add_animation("idle",_retarget(WAIT.get_animation("commuter")))
	animator.add_animation_library("foot",library)
	source.free()
	torso.influence=0.
	skeleton.add_child(torso)
	animator.play("ride_support")
	animator.seek(.2,true)
	gaze.configure(skeleton)
	skeleton.add_child(gaze)
	for side in ["R","L"]:
		hands.append(skeleton.find_bone("Bip01 %s Hand"%side))
		var slot := int(side=="L")
		for suffix in ["1","11","12","2","21","22","4"]:
			digits[slot].append(skeleton.find_bone("Bip01 %s Finger%s"%[side,suffix]))
		var arm:=preload("res://scripts/mentor_arm.gd").new()
		arm.configure(skeleton,side)
		skeleton.add_child(arm)
		arms.append(arm)
	hand_pose.configure(skeleton,animator.get_animation("ride_support"))
	skeleton.add_child(hand_pose)
	skeleton.skeleton_updated.connect(_sample_hand)
	var capsule := CapsuleShape3D.new()
	capsule.height = 1.65
	capsule.radius = .28
	foot_shape.shape = capsule
	foot_shape.position.y = .825
	foot_shape.disabled = true
	add_child(foot_shape)
	floor_snap_length = .5
	floor_max_angle = deg_to_rad(58)
	safe_margin = .012
	collision_layer = 0
	collision_mask = 1 | 4
	add_collision_exception_with(bike)

func _retarget(original: Animation) -> Animation:
	var result := original.duplicate() as Animation
	result.loop_mode = Animation.LOOP_LINEAR
	var rig := str(human.get_path_to(skeleton))
	for i in result.get_track_count():
		var bone := str(result.track_get_path(i).get_concatenated_subnames())
		result.track_set_path(i,NodePath(rig+":"+bone))
	return result

func _animate(clip: String, rate := 1.) -> void:
	if animator.current_animation != clip or not animator.is_playing():
		animator.play(clip,.25)
	animator.speed_scale = rate

func crossing() -> bool:
	return transfer != null and transfer.is_running()

func dismount(at: Vector3, instant := false) -> void:
	mounted = false
	gaze.enabled_on_foot=false
	bike.articulation.set_occupied(false)
	bike.rider_collision.set_deferred("disabled",true)
	global_position = at
	rotation.y = bike.rotation.y+PI
	velocity = Vector3.ZERO
	foot_shape.set_deferred("disabled",false)
	human.reparent(self,true)
	human.show()
	_animate("foot/idle")
	if instant: human.transform = FOOT_FRAME
	else: _transition(FOOT_FRAME,.75)

func board() -> void:
	carrying=false
	for ik in arms: ik.stop()
	torso.influence=0.
	hand_pose.closure=Vector2.ZERO
	release_time=0.
	mounted = true
	gaze.enabled_on_foot=false
	path.clear()
	foot_shape.set_deferred("disabled",true)
	human.reparent(bike.articulation,true)
	animator.play("ride_support",.55)
	_transition(Transform3D.IDENTITY,.82)
	transfer.tween_callback(func():
		bike.articulation.clip = ""
		bike.articulation.set_occupied(true)
		bike.rider_collision.set_deferred("disabled",false))

func _transition(goal: Transform3D, seconds: float) -> void:
	if crossing(): transfer.kill()
	transfer = create_tween().set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	var before := human.transform
	transfer.tween_method(func(t: float): human.transform=before.interpolate_with(goal,t),0.,1.,seconds).set_trans(Tween.TRANS_SINE)

func go(points: PackedVector3Array, final_radius := .14) -> void:
	stop_radius=final_radius
	path = points
	index = 0
	blocked_s = 0.
	blocked_reported = false

func face(point: Vector3, dt: float) -> void:
	gaze.focus=point
	gaze.enabled_on_foot=not mounted
	var d := point-global_position
	if Vector2(d.x,d.z).length()>.02: rotation.y=lerp_angle(rotation.y,atan2(d.x,d.z),minf(1.,dt*8.))

func advance(dt: float, allow: bool, turn_to_path:=true) -> bool:
	if release_time>0.:
		release_time=maxf(0.,release_time-dt)
		var weight:=smoothstep(0.,.38,release_time)
		torso.influence=released_torso*weight
		for ik in arms:
			if ik.is_running():
				ik.influence=weight
				if release_time<=0.: ik.stop()
	if mounted or crossing(): return false
	var move := Vector3.ZERO
	if index < path.size() and allow:
		var d := path[index]-global_position
		d.y = 0
		if d.length() < (stop_radius if index==path.size()-1 else .14): index += 1
		else:
			if turn_to_path:face(path[index],dt)
			move = d.normalized()*minf(1.55,d.length()/dt)
	var before := global_position
	velocity.x = move.x
	velocity.z = move.z
	velocity.y = -.22 if is_on_floor() else velocity.y-22.*dt
	if is_on_floor() and preload("res://scripts/explorer.gd").try_body_step(self,move*dt):
		velocity.x=0.
		velocity.z=0.
	move_and_slide()
	var dist := Vector2(global_position.x-before.x,global_position.z-before.z).length()
	travelled += dist
	blocked_s = blocked_s+dt if move.length()>.3 and dist < dt*.10 else 0.
	if blocked_s==0.: blocked_reported=false
	if dist>dt*.22: _animate("foot/walk",clampf(dist/dt/1.4,.65,1.35))
	else: _animate("foot/idle")
	if carrying:
		load_blend=minf(1.,load_blend+dt/.72)
		var swing:=sin(travelled*4.8)*minf(1.,dist/dt)*.037
		var carry_point:=to_global(Vector3(-.32,.80,.095+swing))
		_arm(0,carry_start.lerp(carry_point,smoothstep(0.,1.,load_blend)),1.)
	shape_right(1. if carrying else maxf(0.,hand_pose.closure.x-dt*4.))
	return index >= path.size()

func begin_carry() -> void:
	carry_start=grip()
	load_blend=0.
	carrying=true

func shape_right(amount: float) -> void:
	hand_pose.forward[0]=(Vector3.DOWN+global_basis.x*.14+global_basis.z*.08).normalized()
	hand_pose.across[0]=global_basis.z
	hand_pose.closure.x=amount

func shape_knock(normal: Vector3,amount: float) -> void:
	hand_pose.forward[1]=(-normal+Vector3.UP*.13).normalized()
	hand_pose.across[1]=(Vector3.UP*.88+normal.cross(Vector3.UP)*.48).normalized()
	hand_pose.closure.y=amount

func _sample_hand() -> void:
	for i in hands.size():
		var wrist := skeleton.to_global(skeleton.get_bone_global_pose(hands[i]).origin)
		var points := PackedVector3Array()
		for bone: int in digits[i]:
			points.append(skeleton.to_global(skeleton.get_bone_global_pose(bone).origin))
		if i==0:
			# The strap lies in the crook between the proximal and middle phalanges.
			var knuckle:Vector3=(points[1]+points[4])*.5
			var root:Vector3=(points[0]+points[3])*.5
			var tips:Vector3=(points[2]+points[5])*.5
			palms[i]=knuckle+(root+tips-knuckle*2.)*.28
			grip_span=(points[0]-points[6]).normalized()
			finger_bend=rad_to_deg((points[4]-points[3]).angle_to(points[5]-points[4]))
		else:
			# Skin projects a few millimetres past the two leading knuckle joints.
			palms[i]=(points[1]+points[4])*.5+hand_pose.forward[1]*.009
		offsets[i]=palms[i]-wrist
		if inspect_joints and not mounted:
			var s:=skeleton.to_global(skeleton.get_bone_global_pose(arms[i].upper).origin)
			var e:=skeleton.to_global(skeleton.get_bone_global_pose(arms[i].elbow).origin)
			var h:=skeleton.to_global(skeleton.get_bone_global_pose(skeleton.find_bone("Bip01 Head")).origin)
			var palm:Vector3=points[3]-wrist
			var key:="L" if i else "R"
			joints_world[key]={"driven":arms[i].is_running() and arms[i].influence>.75,"elbow_deg":rad_to_deg((e-s).angle_to(wrist-e)),"wrist_deg":rad_to_deg((wrist-e).angle_to(palm)),"elbow_above_shoulder_m":e.y-s.y,"wrist_above_shoulder_m":wrist.y-s.y,"head_wrist_m":wrist.distance_to(h),"roll_deg":hand_pose.roll_degrees[i],"reach_error_m":wrist.distance_to(arms[i].wrist_world),"shoulder":str(s),"elbow":str(e),"wrist":str(wrist)}

func grip(left := false) -> Vector3:
	return palms[int(left)]

func reach(point: Vector3, amount: float, left := false) -> void:
	release_time=0.
	var i := int(left)
	if not carrying and arms[1-i].is_running(): arms[1-i].stop()
	torso.goal_world = point
	torso.left_hand = left
	torso.influence = 0. if left else amount
	_arm(i,point,amount)

func _arm(i:int,point:Vector3,amount:float) -> void:
	# A low elbow keeps the forearm below the fist when knocking and below the meal when lifting.
	arms[i].pole_world=to_global(Vector3(.41 if i==1 else -.41,.86,-.11))
	arms[i].wrist_world=point-offsets[i]
	if not arms[i].is_running(): arms[i].start()
	arms[i].influence = amount

func reset_reach() -> void:
	released_torso=torso.influence
	release_time = .38
