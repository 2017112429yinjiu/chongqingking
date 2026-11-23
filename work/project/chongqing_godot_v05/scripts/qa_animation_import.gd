extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var model: Node3D=load(preload("res://scripts/shopkeeper.gd").MODEL_PATH).instantiate()
	root.add_child(model)
	var player: AnimationPlayer=model.find_children("*","AnimationPlayer",true,false)[0]
	var skeleton: Skeleton3D=model.find_children("*","Skeleton3D",true,false)[0]
	var output: Dictionary={"tracks":[],"samples":[],"player_path":str(model.get_path_to(player)),"player_meta":{}}
	for key in player.get_meta_list():output.player_meta[str(key)]=str(player.get_meta(key))
	for clip: String in player.get_animation_list():
		if not clip.to_lower().contains("idle"):continue
		var animation: Animation=player.get_animation(clip)
		for index in range(animation.get_track_count()):
			if str(animation.track_get_path(index)).contains("foot_"):
				output.tracks.append({"path":str(animation.track_get_path(index)),"type":animation.track_get_type(index),"keys":animation.track_get_key_count(index)})
		for t: float in [0,1,2,3,5,7,9,10]:
			player.stop();player.play(clip,0);player.seek(t,true);player.advance(0)
			skeleton.force_update_all_bone_transforms()
			output.samples.append({"t":t,"l":str(skeleton.get_bone_global_pose(skeleton.find_bone("foot_l")).origin),"r":str(skeleton.get_bone_global_pose(skeleton.find_bone("foot_r")).origin)})
	FileAccess.open("res://verification_r18/animation_import_audit.json",FileAccess.WRITE).store_string(JSON.stringify(output,"\t"))
	print("IMPORTED_FEET ",JSON.stringify(output));quit()
