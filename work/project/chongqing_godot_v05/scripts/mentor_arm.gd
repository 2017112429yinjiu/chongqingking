extends SkeletonModifier3D
## Two rigid limb segments. The reference elbow plane comes from this rider on the handlebars.
var upper:int
var elbow:int
var wrist:int
var upper_frame:=Basis.IDENTITY
var fore_frame:=Basis.IDENTITY
var wrist_world:=Vector3.ZERO
var pole_world:=Vector3.ZERO
var working:=false

func frame(along:Vector3,normal:Vector3) -> Basis:
	var x:=along.normalized()
	var y:=(normal-x*x.dot(normal)).normalized()
	return Basis(x,y,x.cross(y))

func configure(sk:Skeleton3D,side:String) -> void:
	var prefix:="Bip01 "+side+" "
	upper=sk.find_bone(prefix+"UpperArm")
	elbow=sk.find_bone(prefix+"Forearm")
	wrist=sk.find_bone(prefix+"Hand")
	var s:=sk.get_bone_global_pose(upper)
	var e:=sk.get_bone_global_pose(elbow)
	var w:=sk.get_bone_global_pose(wrist)
	var a:=e.origin-s.origin
	var b:=w.origin-e.origin
	var normal:=a.cross(b).normalized()
	assert(normal.length_squared()>.95,"Bent calibration pose required")
	upper_frame=frame(a,normal).inverse()*s.basis.orthonormalized()
	fore_frame=frame(b,normal).inverse()*e.basis.orthonormalized()

func start() -> void: working=true
func stop() -> void: working=false
func is_running() -> bool:return working

func _rotate(sk:Skeleton3D,bone:int,target:Basis) -> void:
	var parent:=sk.get_bone_global_pose(sk.get_bone_parent(bone)).basis.orthonormalized()
	var required:=(parent.inverse()*target).orthonormalized().get_rotation_quaternion()
	sk.set_bone_pose_rotation(bone,required)

func _process_modification() -> void:
	if not working:return
	var sk:=get_skeleton()
	var s:=sk.get_bone_global_pose(upper).origin
	var e:=sk.get_bone_global_pose(elbow).origin
	var w:=sk.get_bone_global_pose(wrist).origin
	var a:=s.distance_to(e)
	var b:=e.distance_to(w)
	var dest:=sk.to_local(wrist_world)-s
	var line:=dest.normalized()
	var d:=clampf(dest.length(),maxf(absf(a-b)+.001,(a+b)*.39),(a+b)*.982)
	var pole:=(sk.to_local(pole_world)-s).slide(line).normalized()
	if pole.length_squared()<.5:return
	var f:=(d*d+a*a-b*b)/(2.*d)
	var first:=line*f+pole*sqrt(maxf(0.,a*a-f*f))
	var second:=line*d-first
	var n:=first.cross(second).normalized()
	_rotate(sk,upper,frame(first,n)*upper_frame)
	_rotate(sk,elbow,frame(second,n)*fore_frame)
