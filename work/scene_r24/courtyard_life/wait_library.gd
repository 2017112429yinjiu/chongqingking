extends SceneTree
func _initialize()->void:
	var out:=AnimationLibrary.new()
	var shop:AnimationLibrary=load("res://assets/frontage_r24/stall_clips.res")
	var dst:Node=load("res://assets/block_r23/commuter.glb").instantiate()
	var sk:Node=dst.find_children("*","Skeleton3D",true,false)[0]
	var player:AnimationPlayer=dst.find_children("*","AnimationPlayer",true,false)[0]
	var path:=player.get_node(player.root_node).get_path_to(sk)
	var clip:Animation=shop.get_animation("watch_street").duplicate()
	clip.loop_mode=Animation.LOOP_LINEAR;out.add_animation("neighbor",clip)
	var donor:Node=load("res://assets/courtyard_r24/standing_commuter.glb").instantiate()
	var library:AnimationPlayer=donor.find_children("*","AnimationPlayer",true,false)[0]
	for name_of_clip in library.get_animation_list():
		if name_of_clip=="RESET":continue
		clip=library.get_animation(name_of_clip).duplicate()
		for i in clip.get_track_count():
			var b=clip.track_get_path(i)
			if b.get_subname_count():clip.track_set_path(i,NodePath(str(path)+":"+str(b.get_concatenated_subnames())))
		clip.loop_mode=Animation.LOOP_LINEAR
		out.add_animation("commuter",clip);break
	donor.free();dst.free()
	assert(out.get_animation_list().size()==2)
	var status:=ResourceSaver.save(out,"res://assets/courtyard_r24/wait_clips.res")
	print("COURT14_WAIT ",status," ",out.get_animation_list())
	quit(0 if status==OK else 2)

