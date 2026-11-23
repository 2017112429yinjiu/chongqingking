extends Node3D
## Render-only articulation. The parent controller owns input and collision.
const VEHICLE: PackedScene=preload("res://assets/vehicles/scooter_r18.glb")
const RIDER: PackedScene=preload("res://assets/characters/rider_r18.glb")
const ROLL_RADIUS: float=.236
var vehicle: Node3D
var human: Node3D
var steering: Node3D
var rear_wheel: Node3D
var front_wheel: Node3D
var stand: Node3D
var animator: AnimationPlayer
var face: MeshInstance3D
var blink_shapes: Array[int]=[]
var steer_angle: float=0.0
var support_amount: float=1.0
var roll_phase: float=0.0
var clock: float=0.0
var clip: String=""
var occupied: bool=false
var stopped_time: float=1.0

func _ready() -> void:
	vehicle=VEHICLE.instantiate();add_child(vehicle)
	human=RIDER.instantiate();add_child(human);human.visible=false
	steering=vehicle.find_child("Steering",true,false)
	rear_wheel=vehicle.find_child("WheelRear",true,false)
	front_wheel=vehicle.find_child("WheelFront",true,false)
	stand=vehicle.find_child("Kickstand",true,false)
	animator=human.find_child("AnimationPlayer",true,false)
	for mesh: MeshInstance3D in human.find_children("*","MeshInstance3D",true,false):
		for surface in range(mesh.mesh.get_surface_count()):
			var material: StandardMaterial3D=mesh.mesh.surface_get_material(surface).duplicate()
			if material.resource_name.contains("head"):
				material.subsurf_scatter_enabled=true;material.subsurf_scatter_skin_mode=true;material.subsurf_scatter_strength=.10
			if material.resource_name.contains("opacity"):
				material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
			mesh.set_surface_override_material(surface,material)
		for index in range(mesh.mesh.get_blend_shape_count()):
			var label: String=str(mesh.mesh.get_blend_shape_name(index)).to_lower()
			if label.begins_with("ak_") and "eyeblink" in label:
				face=mesh;blink_shapes.append(index)
	_pose("ride_support",0.0)

func set_occupied(value: bool) -> void:
	occupied=value;human.visible=value
	if value:
		support_amount=1.0;steer_angle=0.0;stopped_time=1.0
		_pose("ride_support",0.0)

func update_motion(delta: float,speed: float,input_steer: float,distance: float) -> void:
	clock+=delta
	# Signed distance is measured after move_and_slide: blocked tyres do not spin.
	roll_phase=fposmod(roll_phase-distance/ROLL_RADIUS,TAU)
	rear_wheel.rotation.x=roll_phase;front_wheel.rotation.x=roll_phase
	stopped_time=stopped_time+delta if absf(speed)<.10 else 0.0
	# Crossing through zero while changing direction must not twitch the foot.
	var wants_support: bool=stopped_time>.18
	support_amount=move_toward(support_amount,1.0 if wants_support else 0.0,delta*1.8)
	var target_steer: float=input_steer*.32 if occupied and support_amount<.01 else 0.0
	steer_angle=move_toward(steer_angle,target_steer,delta*1.4)
	steering.rotation.y=steer_angle
	stand.rotation.z=move_toward(stand.rotation.z,-1.10 if occupied else 0.0,delta*4.0)
	if human.visible:
		_blink()
	if not occupied:return
	if support_amount>.001:
		_pose("ride_support",1.0-support_amount)
	elif absf(steer_angle)>.001:
		_pose("ride_steer",1.0+steer_angle/.32)
	else:
		_pose("ride_idle",fposmod(clock,4.0))

func _blink() -> void:
	var blink_time: float=fposmod(clock+1.6,4.3)
	var blink: float=sin(PI*blink_time/.18) if blink_time<.18 else 0.0
	if is_instance_valid(face):
		for index in blink_shapes:face.set_blend_shape_value(index,blink*.96)

func _pose(name: String,time: float) -> void:
	if clip!=name:
		clip=name;animator.play(name,0)
	# Blender frame 1 is exported at 1/30 s, not zero. Account for it so
	# handlebars and sampled contact poses agree during continuous steering.
	animator.seek(time+1.0/30.0,true);animator.advance(0);animator.pause()
