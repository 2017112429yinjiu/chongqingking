extends SkeletonModifier3D
## Apply a load-bearing grip after locomotion, torso reach and arm IK.
var closure := Vector2.ZERO
var roll_degrees:=Vector2.ZERO
var wrist_roll:=Vector2.ZERO
var forward := [Vector3.DOWN,Vector3.LEFT]
var across := [Vector3.FORWARD,Vector3.UP]
var joints: Array = [[],[]]
var rotations: Array = [[],[]]
var wrists: Array[int] = []
var forearms: Array[int] = []
var middle: Array[int] = []
var index: Array[int] = []
var little: Array[int] = []
var chains: Array = [[],[]]
var thumbs: Array = [[],[]]

func configure(sk: Skeleton3D, pose: Animation) -> void:
	for side in ["R","L"]:
		var prefix := "Bip01 "+str(side)+" "
		forearms.append(sk.find_bone(prefix+"Forearm"))
		wrists.append(sk.find_bone(prefix+"Hand"))
		middle.append(sk.find_bone(prefix+"Finger2"))
		index.append(sk.find_bone(prefix+"Finger1"))
		little.append(sk.find_bone(prefix+"Finger4"))
		var slot:=int(side=="L")
		for digit in range(1,5):
			var digit_name:=prefix+"Finger"+str(digit)
			chains[slot].append([sk.find_bone(digit_name),sk.find_bone(digit_name+"1"),sk.find_bone(digit_name+"2")])
		for suffix in ["0","01","02"]:thumbs[slot].append(sk.find_bone(prefix+"Finger"+suffix))
	for track in pose.get_track_count():
		if pose.track_get_type(track)!=Animation.TYPE_ROTATION_3D: continue
		var bone := str(pose.track_get_path(track).get_concatenated_subnames())
		if not (" Finger" in bone): continue
		var slot := int(" L " in bone)
		joints[slot].append(sk.find_bone(bone))
		rotations[slot].append(pose.rotation_track_interpolate(track,0.))

func axes(f: Vector3,a: Vector3) -> Basis:
	var x:=f.normalized()
	var y:=(a-x*a.dot(x)).normalized()
	return Basis(x,y,x.cross(y))

func _process_modification() -> void:
	var sk := get_skeleton()
	for i in 2:
		var weight := closure[i]
		if weight <= .001:
			wrist_roll[i]=0.
			continue
		var w := sk.get_bone_global_pose(wrists[i])
		var f := sk.get_bone_global_pose(middle[i]).origin-w.origin
		var a := sk.get_bone_global_pose(index[i]).origin-sk.get_bone_global_pose(little[i]).origin
		var inv := sk.global_basis.inverse()
		var aim:Vector3=(inv*forward[i]).normalized()
		var forearm:Vector3=(w.origin-sk.get_bone_global_pose(forearms[i]).origin).normalized()
		var difference:=forearm.angle_to(aim)
		var pointing:=forearm.slerp(aim,minf(1.,deg_to_rad(18.)/maxf(.001,difference)))
		var swing:=Quaternion(f.normalized(),pointing)
		var neutral:Vector3=(swing*a).slide(pointing).normalized()
		var roll_axis:Vector3=(inv*across[i]).slide(pointing).normalized()
		var roll:=clampf(neutral.signed_angle_to(roll_axis,pointing),deg_to_rad(-18.),deg_to_rad(18.))
		wrist_roll[i]=move_toward(wrist_roll[i],roll,deg_to_rad(130.)*minf(get_process_delta_time(),.05))
		roll=wrist_roll[i]
		roll_degrees[i]=rad_to_deg(roll)*weight
		var rotation:=Quaternion(pointing,roll)*swing
		w.basis=Basis(Quaternion.IDENTITY.slerp(rotation,weight))*w.basis
		sk.set_bone_global_pose(wrists[i],w)
		for k in joints[i].size():
			var bone: int = joints[i][k]
			sk.set_bone_pose_rotation(bone,sk.get_bone_pose_rotation(bone).slerp(rotations[i][k],weight))
		var new_axes:=axes(sk.get_bone_global_pose(middle[i]).origin-w.origin,sk.get_bone_global_pose(index[i]).origin-sk.get_bone_global_pose(little[i]).origin)
		var palmward:=new_axes.z*(-1. if i==0 else 1.)
		for chain:Array in chains[i]:
			# Load lies across PIP joints. Curl towards the palm; keep fingertips tucked.
			aim_segment(sk,chain[0],chain[1],new_axes.x*(.62 if i==0 else .92)+palmward*(.78 if i==0 else .39),weight)
			aim_segment(sk,chain[1],chain[2],new_axes.x*(-.67 if i==0 else -.19)+palmward*.81,weight)
			var distal:=sk.get_bone_global_pose(chain[2])
			var previous:=sk.get_bone_global_pose(chain[1])
			var pivot:=new_axes.y*(-1. if i==0 else 1.)
			var incoming:=(distal.origin-previous.origin).normalized()
			var desired:Vector3=(-new_axes.x-palmward*.16).normalized()
			var signed:=incoming.signed_angle_to(desired,pivot)
			distal.basis=Basis(pivot,clampf(signed,-.55,.55)*weight)*distal.basis
			sk.set_bone_global_pose(chain[2],distal)
		# The thumb opposes the outside of the index instead of remaining in a steering grip.
		var thumb:Array=thumbs[i]
		var thumb_base:=sk.get_bone_global_pose(thumb[0]).origin
		var thumb_middle:=sk.get_bone_global_pose(thumb[1]).origin
		var target:=sk.get_bone_global_pose(chains[i][0][1]).origin
		var distance:=thumb_base.distance_to(target)
		target+=new_axes.y*distance*.12+palmward*distance*.10
		aim_segment(sk,thumb[0],thumb[1],(target-thumb_base).normalized()*.72+(thumb_middle-thumb_base).normalized()*.28,weight)
		aim_segment(sk,thumb[1],thumb[2],target-sk.get_bone_global_pose(thumb[1]).origin,weight)

func aim_segment(sk:Skeleton3D,bone:int,child:int,direction:Vector3,weight:float) -> void:
	var pose:=sk.get_bone_global_pose(bone)
	var axis:=(sk.get_bone_global_pose(child).origin-pose.origin).normalized()
	var turn:=Quaternion(axis,direction.normalized())
	pose.basis=Basis(Quaternion.IDENTITY.slerp(turn,weight))*pose.basis
	sk.set_bone_global_pose(bone,pose)
