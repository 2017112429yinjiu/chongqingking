extends SceneTree
func _initialize() -> void:
	for f in ["res://assets/characters/rider_r18.glb","res://assets/block_r23/commuter.glb"]:
		var scene=load(f).instantiate()
		var anim:AnimationPlayer=scene.find_child("AnimationPlayer",true,false)
		var sk:Skeleton3D=scene.find_children("*","Skeleton3D",true,false)[0]
		var a=anim.get_animation(anim.get_animation_list()[0])
		print(f," ",anim.root_node," sk ",scene.get_path_to(sk)," first ",a.track_get_path(0)," rest ",sk.find_bone("Bip01 R Hand")," ", sk.get_bone_name(0))
		scene.free()
	var lib=load("res://assets/courtyard_r24/wait_clips.res")
	print("idle ",lib.get_animation_list()," ",lib.get_animation(lib.get_animation_list()[0]).track_get_path(0))
	quit()
