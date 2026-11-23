extends SceneTree
func _initialize(): call_deferred("test")
func test():
	var model=load("res://assets/characters/court_resident/court_resident.glb").instantiate()
	root.add_child(model)
	var anim=model.find_children("*","AnimationPlayer",true,false)[0]
	var sk=model.find_children("*","Skeleton3D",true,false)[0]
	var idx=sk.find_bone("Bip01 Head")
	print("indices ",idx, " clips ",anim.get_animation_list())
	anim.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	anim.play("sit_look",0)
	for t in [0.,1.,2.,3.,4.,5.,6.]:
		anim.seek(t,true)
		anim.advance(0)
		sk.force_update_all_bone_transforms()
		var x=sk.get_bone_global_pose(idx)
		print("REVIEW ",t," head ",x.basis.get_rotation_quaternion()," move ",x.origin, " local ",sk.get_bone_pose_rotation(idx))
	quit()
