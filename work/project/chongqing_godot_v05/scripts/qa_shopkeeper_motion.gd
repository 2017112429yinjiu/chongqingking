extends RefCounted
## Continuous real-time inspection take. The order is scripted, not user-input QA.
static func run(main: Node3D) -> void:
	var tag: String="r18_motion_review"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--motion-tag="):tag=argument.trim_prefix("--motion-tag=")
	assert(tag.is_valid_identifier())
	var evidence: Dictionary={"character_sha256":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),"counter_sha256":FileAccess.get_sha256("res://assets/characters/serving_counter_r18.glb"),"character_import_sha256":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import"),"capture_start_unix":Time.get_unix_time_from_system(),"scripts":{},"view":"r18_workstation","scripted_order":true}
	for script: String in ["shopkeeper","shopkeeper_attention","gameplay","qa_shopkeeper_motion"]:
		evidence.scripts[script]=FileAccess.get_sha256("res://scripts/"+script+".gd")
	main.hud.visible=false
	main.explorer.go_to_view("r18_workstation")
	main.gameplay.shopkeeper.autonomous=true
	main.gameplay.shopkeeper.attention.tracking=true
	main.gameplay.shopkeeper.attention.target=main.explorer.camera.global_position
	for i in range(330):await main.get_tree().process_frame
	main.gameplay._shop_action()
	for i in range(120):await main.get_tree().process_frame
	main.gameplay._shop_action()
	main.gameplay.shopkeeper.attention.tracking=true
	for i in range(90):await main.get_tree().process_frame
	print("R18_MOTION_TAKE_COMPLETE")
	DirAccess.make_dir_recursive_absolute("res://verification_r18/motion_takes")
	FileAccess.open("res://verification_r18/motion_takes/"+tag+".json",FileAccess.WRITE).store_string(JSON.stringify(evidence,"\t"))
	main.get_tree().quit()
