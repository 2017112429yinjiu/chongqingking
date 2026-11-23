extends RefCounted
## Verify the complete runtime performance, not merely that two bone angles differ.
static func run(main: Node3D) -> void:
	var game: Node3D=main.gameplay
	var npc: Node3D=game.shopkeeper
	npc.autonomous=false
	main.explorer.can_control(false)
	game._shop_action()
	var max_contact_error: float=0.0
	var held_samples: int=0
	var max_step: float=0.0
	var min_lift: float=INF
	var max_lift: float=0.0
	var previous: Vector3=game.bag.global_position
	var samples: Array=[]
	for frame in range(225):
		await main.get_tree().process_frame
		var t: float=npc.animator.current_animation_position
		if npc.packing and t>=npc.GRASP_TIME and t<npc.RELEASE_TIME:
			var error: float=(game.bag.global_position+Vector3.UP*npc.HANDLE_HEIGHT).distance_to(npc.grip_position())
			max_contact_error=maxf(max_contact_error,error)
			held_samples+=1
		var jump: float=previous.distance_to(game.bag.global_position)
		max_step=maxf(max_step,jump)
		var lift: float=game.bag.global_position.y-npc.food_end.y
		min_lift=minf(min_lift,lift)
		max_lift=maxf(max_lift,lift)
		previous=game.bag.global_position
		if frame%15==0:samples.append({"frame":frame,"clip_time":t,"food":str(previous),"packing":npc.packing,"held":npc.held,"released":npc.released})
	var ready: bool=game.order==game.Order.READY and game.bag.visible
	var settled_error: float=game.bag.global_position.distance_to(npc.food_end)
	npc.set_blink(.96)
	var eyelids: int=npc.eyelids.size()
	npc.set_blink(0)
	game._shop_action()
	var pickup: bool=game.order==game.Order.CARRYING and not game.bag.visible
	var tests: Dictionary={"both_eyelids_exported":eyelids==2,"grip_sampled":held_samples>45,"handle_contact_under_5mm":max_contact_error<.005,"no_position_pop_over_30mm":max_step<.03,"bag_lifts_over_60mm":max_lift>.06,"bag_not_below_table_5mm":min_lift>-.005,"settles_on_authored_release":settled_error<.001,"ready_after_performance":ready,"pickup_hides_food":pickup}
	# Sample the actual 10-second recorded idle and its loop, including foot locks.
	npc.attention.tracking=false
	npc.animator.play(npc.available_clips["idle"],0)
	npc.animator.seek(0,true)
	npc.animator.advance(0)
	npc.skeleton.force_update_all_bone_transforms()
	var foot_indices: Array[int]=[npc.skeleton.find_bone("foot_l"),npc.skeleton.find_bone("foot_r")]
	var initial_feet: Array[Vector3]=[]
	for index in foot_indices:initial_feet.append(npc.skeleton.get_bone_global_pose(index).origin)
	var head_index: int=npc.skeleton.find_bone("head")
	var initial_head: Transform3D=npc.skeleton.get_bone_global_pose(head_index)
	var previous_head: Transform3D=initial_head
	var foot_drift: float=0.0
	var head_motion: float=0.0
	var head_step: float=0.0
	for frame in range(660):
		await main.get_tree().process_frame
		npc.skeleton.force_update_all_bone_transforms()
		for i in range(2):foot_drift=maxf(foot_drift,npc.skeleton.get_bone_global_pose(foot_indices[i]).origin.distance_to(initial_feet[i]))
		var head: Transform3D=npc.skeleton.get_bone_global_pose(head_index)
		head_motion=maxf(head_motion,head.origin.distance_to(initial_head.origin))
		head_step=maxf(head_step,head.origin.distance_to(previous_head.origin))
		previous_head=head
	tests["recorded_idle_is_ten_seconds"]=absf(npc.animator.get_animation(npc.available_clips["idle"]).length-10.0)<.05
	tests["idle_foot_lock_under_0_2mm"]=foot_drift<.0002
	tests["idle_has_recorded_motion"]=head_motion>.004
	tests["idle_loop_no_head_pop_over_10mm"]=head_step<.010
	tests["smile_shape_exported"]=npc.smiles.size()==1
	var attention_report: Dictionary=await preload("res://scripts/qa_shopkeeper_attention.gd").run(npc,main)
	tests.merge(attention_report.tests)
	var passed: bool=true
	for value in tests.values():passed=passed and bool(value)
	var report: Dictionary={"passed":passed,"tests":tests,"contact_error_m":max_contact_error,"held_samples":held_samples,"max_step_m":max_step,"max_lift_m":max_lift,"min_lift_m":min_lift,"settled_error_m":settled_error,"eyelids":eyelids,"character_sha256":FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH),"samples":samples,"scope":"Fixed 60 Hz runtime packing, contact and state checks; not artistic approval"}
	report["idle"]={"foot_drift_m":foot_drift,"head_motion_m":head_motion,"max_head_step_m":head_step,"frames":660}
	report["character_import_sha256"]=FileAccess.get_sha256(preload("res://scripts/shopkeeper.gd").MODEL_PATH+".import")
	report["attention"]=attention_report
	report["contact_scope"]="Paper-handle attachment anchor follows a point on the hand bone; finger-surface contact still requires visual review."
	var context=preload("res://scripts/qa_context.gd")
	context.decorate(report,main)
	var directory: String=context.directory("res://verification_r21/current")
	DirAccess.make_dir_recursive_absolute(directory)
	FileAccess.open(directory+"/shopkeeper_performance.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("SHOPKEEPER_PERFORMANCE_QA ",JSON.stringify(report))
	main.get_tree().quit(0 if passed else 2)
