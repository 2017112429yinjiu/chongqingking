extends RefCounted

const PEOPLE_LAYER := 8
const CLEARANCE := .83
var surveyed: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/market_steps_r24/passing_space.json"))

func install(track: Dictionary) -> void:
	if not surveyed.has(track.route):
		return
	track["passing_offset"] = 0.0
	track["passing_speed"] = 0.0
	var body := AnimatableBody3D.new()
	body.name = "WalkingResident"
	body.collision_layer = PEOPLE_LAYER
	body.collision_mask = 0
	body.sync_to_physics = false
	var volume := CapsuleShape3D.new()
	volume.height = 1.58
	volume.radius = .29
	var shape := CollisionShape3D.new()
	shape.shape = volume
	shape.position.y = .85
	body.add_child(shape)
	track.node.add_child(body)

func lateral_step(track:Dictionary, origin:Vector3, forward:Vector3, length:float,
		dt:float, explorer:Node3D, population:Array[Dictionary]) -> Vector3:
	var side := forward.cross(Vector3.UP)
	var offset:float = track.passing_offset
	var goal:=0.0
	var player:Vector3 = explorer.body.global_position - origin
	var near:bool = explorer.walking and absf(player.y)<.64 and player.length_squared()<8.4
	if near and track.d>1.7 and track.d<length-1.7:
		var samples:Array = surveyed[track.route]["forward" if track.sign>0. else "backward"]
		var i:=clampi(floori(track.d/length*(samples.size()-1)),0,samples.size()-2)
		var across:=player.dot(side)
		var which:=1 if across<0. else 0
		var limit:=minf(float(samples[i][which]),float(samples[i+1][which]))
		var along:=absf(player.dot(forward))
		var wanted:=maxf(0.,CLEARANCE-absf(across))
		goal = minf(limit,wanted)*(1. if which==1 else -1.)*(1.-smoothstep(1.25,2.65,along))
		if absf(goal)>.03:
			var foot:=origin+side*goal
			for other in population:
				if other.node==track.node or other.car:continue
				var delta:Vector3=other.node.global_position-foot
				if absf(delta.y)<.8 and Vector2(delta.x,delta.z).length_squared()<.54*.54:
					goal=0.0
					break
	var next:=move_toward(offset,goal,dt*.76)
	track.passing_speed=(next-offset)/dt if dt>0. else 0.
	track.passing_offset=next
	return side*next
