extends SkeletonModifier3D
## Aim the face from the actual eye line; the idle clip occasionally glances sideways.
var focus := Vector3.ZERO
var eyes := PackedInt32Array()
var chain := PackedInt32Array()
var enabled_on_foot:=false

func configure(sk:Skeleton3D) -> void:
	for name_ in ["Bip01 REye","Bip01 LEye"]:eyes.append(sk.find_bone(name_))
	for name_ in ["Bip01 Spine2","Bip01 Neck","Bip01 Head"]:chain.append(sk.find_bone(name_))

func _process_modification() -> void:
	if not enabled_on_foot:return
	var sk:=get_skeleton()
	for i in chain.size():
		var right:=sk.to_global(sk.get_bone_global_pose(eyes[0]).origin)
		var left:=sk.to_global(sk.get_bone_global_pose(eyes[1]).origin)
		var front:=Vector3.UP.cross(right-left).normalized()
		var target:=(focus-(right+left)*.5).slide(Vector3.UP).normalized()
		if front.length_squared()<.9 or target.length_squared()<.9:return
		var yaw:=front.signed_angle_to(target,Vector3.UP)
		var limit:float=[.22,.46,.74][i]
		var fraction:float=[.2,.55,1.][i]
		var pose:=sk.get_bone_global_pose(chain[i])
		pose.basis=Basis((sk.global_basis.inverse()*Vector3.UP).normalized(),clampf(yaw*fraction,-limit,limit))*pose.basis
		sk.set_bone_global_pose(chain[i],pose)
