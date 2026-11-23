extends Node3D

const MODEL = "res://assets/characters/court_resident/court_resident.glb"
const FIT = "res://assets/characters/court_resident/bench_fit.json"
const REST = &"sit_rest"
const LOOK = &"sit_look"
enum Distance { NEAR, MID, FAR }
var tier := Distance.NEAR
var animator: AnimationPlayer
var model: Node3D
var game: Node3D
var target: Node3D
var frozen := false
var clock := 4.0
var look_remaining := 0.0
var sample_elapsed := 0.0
var observer_elapsed := 1.0
var greetings := 0
var face: MeshInstance3D
var eyelids: Array[int] = []
var smile: Array[int] = []

func setup(host: Node3D, still: bool) -> void:
	game = host
	frozen = still
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FIT))
	position = Vector3(spec.position[0],spec.position[1],spec.position[2])
	rotation.y = spec.yaw
	model = load(MODEL).instantiate()
	add_child(model)
	for part: MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
		if part.get_blend_shape_count()>0:
			face=part
			break
	for key: StringName in [&"AK_09_EyeBlinkLeft",&"AK_10_EyeBlinkRight"]:
		eyelids.append(face.find_blend_shape_by_name(key))
	for key: StringName in [&"AK_44_MouthSmileLeft",&"AK_45_MouthSmileRight"]:
		smile.append(face.find_blend_shape_by_name(key))
	assert(not eyelids.has(-1) and not smile.has(-1))
	animator = model.find_children("*","AnimationPlayer",true,false)[0]
	animator.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for clip: StringName in [REST,LOOK]:
		assert(animator.has_animation(clip),str(clip))
	pose(REST,clock)
	var obstacle := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.height = .87
	capsule.radius = .205
	shape.shape = capsule
	shape.position = Vector3(0,.82,.005)
	obstacle.add_child(shape)
	add_child(obstacle)
	var point := to_global(Vector3(0,1.10,.36))
	target = game._target("residents.court.neighbor",point,func():return "向街坊问路",func():return not game.actor.seated,ask_directions)
	target.radius = 1.50

func pose(clip: StringName, seconds: float) -> void:
	animator.stop(true)
	animator.play(clip,0)
	animator.seek(clampf(seconds,0,animator.get_animation(clip).length),true)
	animator.advance(0)
	expression(seconds,0.)

func lid_amount(seconds: float) -> float:
	var phase:=fposmod(seconds,15.6)
	for beginning: float in [2.36,7.71,12.15]:
		var age:=phase-beginning
		if age>=0. and age<.21:
			return smoothstep(0.,.075,age)*(1.-smoothstep(.085,.21,age))
	return 0.

func expression(seconds: float,warmth: float) -> void:
	face.set_blend_shape_value(eyelids[0],lid_amount(seconds))
	face.set_blend_shape_value(eyelids[1],lid_amount(seconds-.01))
	for index in smile:face.set_blend_shape_value(index,warmth)

func update_distance(metres: float) -> void:
	match tier:
		Distance.NEAR:
			if metres > 70.: tier=Distance.FAR
			elif metres > 27.: tier=Distance.MID
		Distance.MID:
			if metres < 22.: tier=Distance.NEAR
			elif metres > 70.: tier=Distance.FAR
		Distance.FAR:
			if metres < 22.: tier=Distance.NEAR
			elif metres < 65.: tier=Distance.MID
	model.visible = tier != Distance.FAR

func ask_directions() -> void:
	greetings += 1
	look_remaining = animator.get_animation(LOOK).length
	clock = 0.0
	animator.play(LOOK,.28)
	if game.order == game.Order.CARRYING:
		game._say("街坊：送小面的呀？去山城里小院一号，到了门口按门铃。")
	else:
		game._say("街坊：找面馆呀？从这儿往下走，红招牌那家就是梯坎小面。")
	game.toast_time = 5.5

func _process(delta: float) -> void:
	if frozen or animator == null: return
	clock += delta
	look_remaining = maxf(0,look_remaining-delta)
	observer_elapsed += delta
	if observer_elapsed >= .25:
		observer_elapsed = 0
		update_distance(global_position.distance_to(game.actor.camera.global_position))
	if tier == Distance.FAR: return
	sample_elapsed += delta
	if tier == Distance.MID and sample_elapsed < .18: return
	var rest_length := animator.get_animation(REST).length
	var look_length := animator.get_animation(LOOK).length
	var time_in_cycle := fmod(clock,rest_length+look_length)
	var clip := REST
	var phase := time_in_cycle
	if look_remaining > 0:
		clip=LOOK
		phase=look_length-look_remaining
	elif time_in_cycle>=rest_length:
		clip=LOOK
		phase=time_in_cycle-rest_length
	if animator.current_animation!=clip:
		animator.play(clip,.28)
	animator.seek(maxf(0,phase-sample_elapsed),false)
	animator.advance(sample_elapsed)
	var greeting_age:=look_length-look_remaining
	var warmth:=.16*smoothstep(.12,.68,greeting_age)*(1.-smoothstep(1.8,3.2,greeting_age))
	expression(clock,warmth if look_remaining>0. else 0.)
	sample_elapsed=0
