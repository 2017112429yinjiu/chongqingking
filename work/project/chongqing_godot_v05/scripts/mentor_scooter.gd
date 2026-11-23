extends "res://scripts/scooter_controller.gd"
## The instructor uses the same tyres, steering and world collisions as the learner.
const GUIDE_LAYER := 16
const WAIT_GAP := 10.5
const REJOIN_GAP := 6.5
var learner: CharacterBody3D
var path := PackedVector3Array()
var next_point := 0
var waiting := false
var arrived := false
var escort := true
var trip_number:=0

func _ready() -> void:
	super()
	collision_layer = GUIDE_LAYER
	collision_mask |= 4
	articulation.set_occupied(true)
	rider_collision.disabled = false
	# Rider materials are local duplicates made by scooter_visual.
	for mesh: MeshInstance3D in articulation.human.find_children("*","MeshInstance3D",true,false):
		for surface in mesh.mesh.get_surface_count():
			var original: Material = mesh.mesh.surface_get_material(surface)
			if original and original.resource_name == "Rider_Helmet_Teal":
				var helmet := mesh.get_surface_override_material(surface) as StandardMaterial3D
				if helmet: helmet.albedo_color = Color("d9ab4c")

func has_driver() -> bool:
	return articulation.occupied

func guide_to(points: PackedVector3Array) -> void:
	trip_number+=1
	path = points
	next_point = 0
	arrived = false
	waiting = false

func drive_input() -> Vector3:
	var stop := Vector3(0,0,1)
	if not learner or path.is_empty() or arrived:
		return stop
	var gap := global_position.distance_to(learner.global_position)
	if not escort:
		waiting=false
	elif not is_instance_valid(learner.rider) or gap > WAIT_GAP:
		waiting = true
	elif gap <= REJOIN_GAP:
		waiting = false
	if waiting:
		return stop
	var goal := path[next_point] - global_position
	goal.y = 0
	var final := next_point == path.size()-1
	if goal.length() < (1.0 if final else 1.2):
		if final:
			if absf(speed) < .1:
				arrived = true
				park()
			return stop
		next_point += 1
		return drive_input()
	var heading := -global_basis.z
	var turn := heading.signed_angle_to(goal.normalized(),Vector3.UP)
	var desired_speed := 2.7 if gap < 7 else 1.7
	if absf(turn) > .35: desired_speed = minf(desired_speed,1.6)
	if final: desired_speed = minf(desired_speed,clampf(goal.length()*.8,.65,2.7))
	return Vector3(float(speed < desired_speed),clampf(turn*2.2,-1.,1.),float(speed > desired_speed+.4))
