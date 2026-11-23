extends RefCounted
static func run(main: Node3D) -> void:
	var npc: Node3D=main.gameplay.shopkeeper
	var animator: AnimationPlayer=npc.animator
	var skeleton: Skeleton3D=npc.find_children("*","Skeleton3D",true,false)[0]
	var bone: int=skeleton.find_bone("upperarm_l")
	var poses: Array=[]
	var rotations: Array[Quaternion]=[]
	for clip in ["idle","serve"]:
		animator.stop()
		animator.play(npc.available_clips[clip],0)
		animator.seek(1.0,true)
		animator.advance(0)
		animator.pause()
		await main.get_tree().process_frame
		skeleton.force_update_all_bone_transforms()
		rotations.append(skeleton.get_bone_pose_rotation(bone))
		poses.append({"clip":clip,"arm_rotation":str(rotations[-1]),"time":1.0})
	var angle: float=rotations[0].angle_to(rotations[1])
	var report: Dictionary={"passed":angle>.2,"upper_arm_change_radians":angle,"clips":poses,"asset_sha256":FileAccess.get_sha256("res://assets/characters/shopkeeper_r17.glb"),"bone_count":skeleton.get_bone_count()}
	FileAccess.open("res://verification_r17/character_animation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("CQ_CHARACTER_QA ",JSON.stringify(report))
	main.get_tree().quit(0 if report.passed else 2)
