extends SkeletonModifier3D
## Bend at the lumbar joint before the hand solver, keeping both feet planted.
var goal_world := Vector3.ZERO
var left_hand := false

func _process_modification() -> void:
	var sk := get_skeleton()
	var shoulder := sk.find_bone("Bip01 L UpperArm" if left_hand else "Bip01 R UpperArm")
	var spine := sk.find_bone("Bip01 Spine")
	var shoulder_world := sk.to_global(sk.get_bone_global_pose(shoulder).origin)
	var hip_world := sk.to_global(sk.get_bone_global_pose(spine).origin)
	var direction := goal_world - hip_world
	direction.y = 0.
	if direction.length_squared() < .001:return
	var axis := (sk.global_basis.inverse()*Vector3.UP.cross(direction.normalized())).normalized()
	var lower:=clampf((shoulder_world.y-goal_world.y)/.40,0.,1.)
	var bend:=clampf((shoulder_world.distance_to(goal_world)-.42)*2.55,0.,lerpf(.16,.69,lower))
	var pose := sk.get_bone_global_pose(spine)
	# On this rig both thighs branch from Spine. Preserve their animated world poses.
	var left := sk.find_bone("Bip01 L Thigh")
	var right := sk.find_bone("Bip01 R Thigh")
	var left_pose := sk.get_bone_global_pose(left)
	var right_pose := sk.get_bone_global_pose(right)
	pose.basis = Basis(axis,bend)*pose.basis
	sk.set_bone_global_pose(spine,pose)
	sk.set_bone_global_pose(left,left_pose)
	sk.set_bone_global_pose(right,right_pose)
