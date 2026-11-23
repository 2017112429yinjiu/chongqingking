extends SceneTree

func _initialize() -> void:
	call_deferred("take")

func take() -> void:
	var main := load("res://main.tscn").instantiate() as Node3D
	root.add_child(main)
	current_scene=main
	while main.gameplay==null or main.gameplay.court_resident==null:
		await physics_frame
	main.hud.visible=false
	main.explorer.go_to_view("r20_neighbor")
	var resident: Node3D=main.gameplay.court_resident
	for i in range(30):await process_frame
	var start:=Engine.get_process_frames()
	for i in range(45):await process_frame
	resident.ask_directions()
	for i in range(217):await process_frame
	var evidence:={"first_frame":start,"take_frames":262,"fps":30,"requested_dimensions":[1280,720],"view":"r20_neighbor","greeting_trigger_frame":45,"trigger":"Scripted greeting on the actual resident controller. No recorded player input or voice.","scene":main.scene_identity.court_resident,"profile_sha256":FileAccess.get_sha256(main.art_profile_path)}
	var path:="res://verification_r20/current/resident_motion"
	DirAccess.make_dir_recursive_absolute(path)
	FileAccess.open(path+"/take.json",FileAccess.WRITE).store_string(JSON.stringify(evidence,"\t"))
	quit()
