extends RefCounted

static func run(main: Node3D,tests: Array) -> void:
	var resident: Node3D=main.gameplay.court_resident
	var game: Node3D=main.gameplay
	var actor: Node3D=game.actor
	var world:=main.get_world_3d().direct_space_state
	var check:=func(label: String,passed: bool):tests.append({"name":label,"pass":passed})
	check.call("resident_registered_with_two_clips",resident!=null and resident.animator.has_animation(&"sit_rest") and resident.animator.has_animation(&"sit_look"))
	if not resident: return
	var fit: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(resident.FIT))
	for key: String in ["seat","left","right"]:
		var raw: Array=fit.skin_samples[key]
		var point:=Vector3(raw[0],raw[1],raw[2])
		var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.09,point-Vector3.UP*.10,1))
		check.call("resident_collision_support_"+key,not hit.is_empty() and absf(hit.position.y-point.y)<.05)
	var anchor:=resident.to_global(Vector3(0,0,1.06))
	var ground:=world.intersect_ray(PhysicsRayQueryParameters3D.create(anchor+Vector3.UP,anchor-Vector3.UP,1))
	if ground.is_empty():
		check.call("resident_approach_has_ground",false)
		return
	actor.body.global_position=ground.position+Vector3.UP*.06
	await main.get_tree().physics_frame
	check.call("ask_neighbor_on_foot",game.manager.select()==resident.target and game.interact() and resident.greetings==1 and game.toast.contains("面馆"))
	check.call("greeting_keeps_order",game.order==0 and game.earnings==0 and resident.look_remaining>0.)
	for letter in game.toast:
		if letter.unicode_at(0)>127 and not main.UI_FONT.has_char(letter.unicode_at(0)):check.call("resident_missing_glyph_"+letter,false)
	var phase_before: float=resident.clock
	resident.expression(2.444,.12)
	check.call("resident_eyelids_and_smile_deform",resident.face.get_blend_shape_value(resident.eyelids[0])>.98 and resident.face.get_blend_shape_value(resident.eyelids[1])>.96 and absf(resident.face.get_blend_shape_value(resident.smile[0])-.12)<.002)
	resident.expression(3.,0.)
	check.call("resident_eyes_reopen",resident.face.get_blend_shape_value(resident.eyelids[0])==0. and resident.face.get_blend_shape_value(resident.eyelids[1])==0.)
	resident.update_distance(80)
	check.call("resident_far_hides_skin",not resident.model.visible and resident.tier==resident.Distance.FAR)
	resident.update_distance(68)
	check.call("resident_far_hysteresis",not resident.model.visible)
	resident.update_distance(42)
	check.call("resident_middle_keeps_entity",resident.model.visible and resident.tier==resident.Distance.MID and game.court_resident==resident)
	resident.update_distance(20)
	check.call("resident_near_keeps_clock_and_greeting",resident.tier==resident.Distance.NEAR and resident.greetings==1 and resident.clock==phase_before)
	var previous_order: int=game.order
	game.order=game.Order.CARRYING
	check.call("delivery_question_names_destination",game.interact() and game.toast.contains("小院一号") and game.order==game.Order.CARRYING and resident.greetings==2)
	game.order=previous_order
	var skeleton:=resident.model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var head:=skeleton.find_bone("Bip01 Head")
	if head<0:head=skeleton.find_bone("Bip01_Head")
	if head>=0:
		resident.pose(&"sit_look",0.)
		skeleton.force_update_all_bone_transforms()
		var before:=skeleton.get_bone_global_pose(head).basis.orthonormalized().get_rotation_quaternion()
		var largest:=0.
		for time in [1.,2.,3.,4.,5.,6.]:
			resident.pose(&"sit_look",time)
			skeleton.force_update_all_bone_transforms()
			largest=maxf(largest,before.angle_to(skeleton.get_bone_global_pose(head).basis.orthonormalized().get_rotation_quaternion()))
		check.call("resident_imported_head_turns",largest>deg_to_rad(8.))
	else:check.call("resident_head_bone",false)
	actor.body.global_position+=Vector3.RIGHT*7.
	check.call("resident_greeting_range_limited",not game.manager.reachable(resident.target))
