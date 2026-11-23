extends SkeletonModifier3D
## A bounded additive head turn after animation; the torso stays at the counter.
var host: Node3D
var target: Vector3
var tracking: bool=false
var yaw: float=0.0
var pitch: float=0.0
var eye_offsets: Dictionary={}

func _process_modification_with_delta(delta: float) -> void:
	var skeleton: Skeleton3D=get_skeleton()
	if not skeleton or not host: return
	var wanted: float=0.0
	var wanted_pitch: float=0.0
	var index: int=skeleton.find_bone("head")
	var pose: Transform3D=skeleton.get_bone_global_pose(index)
	if tracking:
		var local: Vector3=host.to_local(target)
		wanted=clampf(atan2(local.x,local.z),-.46,.46) if local.z>0 else 0.0
		var head_local: Vector3=host.to_local(skeleton.to_global(pose.origin))
		var offset: Vector3=local-head_local
		if local.z>0:wanted_pitch=clampf(-atan2(offset.y,Vector2(offset.x,offset.z).length()),-.18,.28)
	yaw=lerpf(yaw,wanted,1-exp(-delta*4.5))
	pitch=lerpf(pitch,wanted_pitch,1-exp(-delta*4.5))
	var local_right: Vector3=(skeleton.global_basis.inverse()*host.global_basis.x).normalized()
	pose.basis=Basis(Vector3.UP,yaw)*Basis(local_right,pitch)*pose.basis
	skeleton.set_bone_global_pose(index,pose)
	# Each eyeball pivots in its own socket and converges on the observer.
	# Bone local +Y follows the authored forward axis, independent of import axes.
	for name: String in ["eye_l","eye_r"]:
		var eye_index: int=skeleton.find_bone(name)
		if eye_index<0:continue
		var eye: Transform3D=skeleton.get_bone_global_pose(eye_index)
		var rotation: Quaternion=Quaternion.IDENTITY
		if tracking and host.to_local(target).z>0:
			var direction: Vector3=(skeleton.to_local(target)-eye.origin).normalized()
			var forward: Vector3=eye.basis.y.normalized()
			rotation=Quaternion(forward,direction)
			var angle: float=rotation.get_angle()
			if angle>.30:rotation=Quaternion.IDENTITY.slerp(rotation,.30/angle)
		var previous: Quaternion=eye_offsets.get(name,Quaternion.IDENTITY)
		var offset: Quaternion=previous.slerp(rotation,1-exp(-delta*24.0))
		eye_offsets[name]=offset
		eye.basis=Basis(offset)*eye.basis
		skeleton.set_bone_global_pose(eye_index,eye)
