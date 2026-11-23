extends SceneTree
## Record a complete order at the working counter with a fixed customer-side camera.
func _initialize() -> void:
	call_deferred("take")

func xyz(v: Vector3) -> Array:
	return [v.x,v.y,v.z]

func take() -> void:
	var directory: String=preload("res://scripts/qa_context.gd").directory("res://verification_r21/current")
	DirAccess.make_dir_recursive_absolute(directory)
	var main := load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null or main.gameplay.shopkeeper==null:
		await physics_frame
	var game: Node3D=main.gameplay
	var npc: Node3D=game.shopkeeper
	var fingers=preload("counter_fingertip_audit.gd").new()
	fingers.setup(npc)
	main.hud.visible=false
	main.explorer.go_to_view("r18_player_eye")
	var cam:=Camera3D.new()
	main.add_child(cam)
	cam.global_position=npc.to_global(Vector3(.57,1.53,1.56))
	cam.look_at(npc.to_global(Vector3(-.02,1.17,.16)))
	cam.fov=45
	cam.make_current()
	for i in range(35):await process_frame
	var samples: Array=[]
	var frames: int=150
	for i in range(frames):
		if i==16:game._shop_action()
		await process_frame
		if i>=16 and i<115:
			var row: Dictionary={"frame":i,"t":npc.animator.current_animation_position,"bag":xyz(npc.to_local(game.bag.global_position))}
			if row.t>=1.19 and row.t<=2.46:
				row["skin"]=fingers.clearances(npc,game.bag)
			for bone: String in ["hand_l","hand_r","index_03_l","middle_03_l","thumb_03_l","apron_L","apron_R","foot_l","foot_r"]:
				var index: int=npc.skeleton.find_bone(bone)
				row[bone]=xyz(npc.to_local(npc.skeleton.to_global(npc.skeleton.get_bone_global_pose(index).origin)))
			samples.append(row)
	FileAccess.open(directory+"/counter_take.json",FileAccess.WRITE).store_string(JSON.stringify({"sample_fps":30,"frames":frames,"trigger_frame":16,"camera_local":[.57,1.53,1.56],"scripted_order":true,"distal_vertices":fingers.points.size(),"profile_sha256":FileAccess.get_sha256(main.art_profile_path),"samples":samples},"\t"))
	quit()
