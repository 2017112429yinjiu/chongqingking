extends SceneTree

func _initialize() -> void:
	call_deferred("extract")

func extract() -> void:
	var source := (load("res://dev_stall_motion/animations.glb") as PackedScene).instantiate()
	var target := (load("res://assets/block_r23/neighbor.glb") as PackedScene).instantiate()
	root.add_child(source)
	root.add_child(target)
	var player := source.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var receiver := target.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var anchor := receiver.get_node(receiver.root_node)
	var lib := AnimationLibrary.new()
	print("EXTRACT ",player.get_animation_list())
	for key in ["watch_street","greet"]:
		var match_key: String=""
		for label in player.get_animation_list():
			if str(label).to_lower().contains(key):match_key=label
		if match_key.is_empty():
			push_error("Missing %s"%key)
			quit(2)
			return
		var clip:=player.get_animation(match_key).duplicate() as Animation
		clip.loop_mode=Animation.LOOP_LINEAR if key=="watch_street" else Animation.LOOP_NONE
		for i in clip.get_track_count():
			var path:=clip.track_get_path(i)
			var node:=anchor.get_node_or_null(NodePath(path.get_concatenated_names()))
			if not node or (node is Skeleton3D and path.get_subname_count()>0 and node.find_bone(path.get_subname(0))<0):
				push_error("Unbound track %s"%path)
				quit(2)
				return
		lib.add_animation(key,clip)
	var err:=ResourceSaver.save(lib,"res://assets/frontage_r24/stall_clips.res",ResourceSaver.FLAG_COMPRESS)
	print("STALL_LIB ",lib.get_animation_list()," ",err)
	quit(0 if err==OK else 2)

