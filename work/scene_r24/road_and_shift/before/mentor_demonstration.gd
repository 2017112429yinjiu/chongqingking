extends Node3D

enum Action { AT_BIKE, BOARD_FIRST, RIDING, SHOP_EXIT, WALK_COUNTER, ORDER, PACK, PICK_UP, LIFT_CLEAR, PUPIL_PICKUP, RETURN_BIKE, LOAD_BOX, BOARD_AGAIN, YARD_EXIT, UNLOAD, PUPIL_UNLOAD, LEAD_HOME, KNOCK, WALK_TO_HOOK, HANG, RELEASE_HOOK, STEP_ASIDE, PUPIL_DELIVERS }
const HANDLE := .331
const BOX_TIME:=4.8
const BAG = preload("res://scripts/takeaway_bag.gd")
const Walker = preload("res://scripts/mentor_walker.gd")
var lesson: Node3D
var game: Node3D
var bike: CharacterBody3D
var walker: CharacterBody3D
var parcel: Node3D
var mentor_box := preload("res://scripts/shift_cargo_box.gd").new()
var pupil_box := preload("res://scripts/shift_cargo_box.gd").new()
var transfer_time := -1.
var loading_pupil := false
var pupil_initial_grip := Vector3.ZERO
var pupil_hand: BoneAttachment3D
var pupil_pose := preload("res://scripts/mentor_hands.gd").new()
var pupil_ik := SkeletonIK3D.new()
var pupil_goal := Node3D.new()
var pupil_hang_ik := SkeletonIK3D.new()
var pupil_hang_goal := Node3D.new()
var pupil_hang_time := -1.
var pupil_hang_start := Vector3.ZERO
var pupil_right_wrist := Vector3.ZERO
var pupil_grasp := Vector3.ZERO
var pupil_knuckle := Vector3.ZERO
var pupil_wrist := Vector3.ZERO
var pupil_strikes := PackedFloat32Array()
var pupil_yaw := 0.
var old_target := Vector3.ZERO
var old_radius := 0.
var hooks: Array[Vector3] = []
var supports: Array[String] = []
var bell: Node3D
var door := preload("res://scripts/teaching_door.gd").new()
var knock_distances := PackedFloat32Array()
var knock_retractions := PackedFloat32Array()
var peak_retraction := 0.
var knock_index := 0
var carry_sway := 0.
var grip_offset := 0.
var stepped_in:=false
var meal_transfer_started:=false
var action := Action.AT_BIKE
var timer := 0.
var in_hand := false
var packed_on_bike := false
var student_hooked := false
var student_knocked := false
var student_stowed := false
var student_retrieved := false
var waiting_for_view := false
var notes: Array[String] = []
var hand_start := Vector3.ZERO
var latest_grasp_error := -1.
var grasp_angle := 0.
var latest_hook_error := -1.
var shop_shown := false
var door_shown := false
var walking_wait := false

func setup(controller: Node3D) -> void:
	lesson = controller
	game = lesson.game
	bike = lesson.mentor
	mentor_box.install(bike)
	pupil_box.install(game.scooter)
	walker = Walker.new()
	walker.name = "PengOnFoot"
	add_child(walker)
	walker.setup(bike)
	parcel = BAG.new()
	parcel.name = "PengOrder001"
	add_child(parcel)
	parcel.write_ticket(1,false)
	parcel.hide()
	for target in game.manager.targets:
		if target.interaction_id.begins_with("doorbell.A04.") and (not bell or target.global_position.distance_squared_to(game.destination.global_position)<bell.global_position.distance_squared_to(game.destination.global_position)):
			bell=target
	if game.actor.body_view:
		var sk:Skeleton3D=game.actor.body_view.find_children("*","Skeleton3D",true,false)[0]
		pupil_hand=BoneAttachment3D.new()
		pupil_hand.bone_name="Bip01 R Finger2"
		sk.add_child(pupil_hand)
		add_child(pupil_goal)
		pupil_ik.root_bone="Bip01 L UpperArm"
		pupil_ik.tip_bone="Bip01 L Hand"
		pupil_ik.override_tip_basis=false
		pupil_ik.min_distance=.12
		sk.add_child(pupil_ik)
		pupil_ik.target_node=pupil_ik.get_path_to(pupil_goal)
		add_child(pupil_hang_goal)
		pupil_hang_ik.root_bone="Bip01 R UpperArm"
		pupil_hang_ik.tip_bone="Bip01 R Hand"
		pupil_hang_ik.override_tip_basis=false
		pupil_hang_ik.min_distance=.12
		sk.add_child(pupil_hang_ik)
		pupil_hang_ik.target_node=pupil_hang_ik.get_path_to(pupil_hang_goal)
		pupil_pose.configure(sk,walker.animator.get_animation("ride_support"))
		sk.add_child(pupil_pose)
		sk.skeleton_updated.connect(_sample_pupil.bind(sk))
	old_target=game.destination.global_position
	old_radius=game.destination.radius
	if not door.locate(game.owner_scene.get_node("City")): push_error("A04 timber door face missing")
	_make_hooks()
	process_priority = 20

func _sample_pupil(sk:Skeleton3D) -> void:
	var pos:=func(b:String)->Vector3:return sk.to_global(sk.get_bone_global_pose(sk.find_bone("Bip01 "+b)).origin)
	pupil_wrist=pos.call("L Hand")
	pupil_right_wrist=pos.call("R Hand")
	pupil_knuckle=(pos.call("L Finger11")+pos.call("L Finger21"))*.5+pupil_pose.forward[1]*.009
	var k:Vector3=(pos.call("R Finger11")+pos.call("R Finger21"))*.5
	pupil_grasp=k+((pos.call("R Finger1")+pos.call("R Finger2")+pos.call("R Finger12")+pos.call("R Finger22"))*.5-k*2.)*.28
	var across:Vector3=pos.call("R Finger1")-pos.call("R Finger4")
	if Vector2(across.x,across.z).length()>.003:pupil_yaw=atan2(-across.z,across.x)

func animate_pupil_knock(t:float) -> void:
	if not pupil_hand:return
	if t<0.:
		pupil_ik.stop()
		pupil_pose.closure.y=0.
		return
	pupil_pose.forward[1]=(-door.NORMAL+Vector3.UP*.13).normalized()
	pupil_pose.across[1]=(Vector3.UP*.88+door.NORMAL.cross(Vector3.UP)*.48).normalized()
	var w:=smoothstep(0.,.44,t)*(1.-smoothstep(1.81,2.10,t))
	pupil_pose.closure.y=w
	pupil_goal.global_position=door.point+door.NORMAL*door.clearance(t)-(pupil_knuckle-pupil_wrist)
	if not pupil_ik.is_running():pupil_ik.start()
	pupil_ik.influence=w

func aim_delivery_target() -> void:
	game.destination.global_position=hooks[1] if student_knocked else door.point+door.NORMAL*.012
	game.destination.radius=.94 if student_knocked else .78

func looking_at_fixture(p:Vector3) -> bool:
	var camera:Camera3D=game.actor.camera
	var direction:=camera.global_position.direction_to(p)
	var in_reach:bool=student_knocked or Vector2(camera.global_position.x-p.x,camera.global_position.z-p.z).length()<.59
	return in_reach and (-camera.global_basis.z).dot(direction)>.84 and game.manager.reachable(game.destination)

func _make_hooks() -> void:
	var metal := StandardMaterial3D.new()
	metal.albedo_color = Color("777c77")
	metal.metallic = .66
	metal.roughness = .54
	for x: float in [-54.70,-54.28]:
		var start := Vector3(x,bell.global_position.y-.09,19.5)
		var hit := get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,start+Vector3.FORWARD*1.65,1))
		if hit.is_empty():
			push_error("Missing entrance wall for delivery hook")
			return
		var n: Vector3 = hit.normal
		var point: Vector3 = hit.position
		supports.append(str(hit.collider.get_path()))
		var mount := Node3D.new()
		add_child(mount)
		mount.global_position = point
		mount.basis = Basis.looking_at(n,Vector3.UP,true)
		for pair in [[Vector3(0,0,.012),Vector3(.07,.115,.028)],[Vector3(0,-.021,.061),Vector3(.017,.018,.11)],[Vector3(0,.002,.11),Vector3(.017,.057,.017)]]:
			var piece := MeshInstance3D.new()
			var box := BoxMesh.new()
			box.size=pair[1];piece.mesh=box;piece.material_override=metal
			mount.add_child(piece);piece.position=pair[0]
		hooks.append(mount.to_global(Vector3(0,-.012,.085)))

func begin_action(a: Action, duration := 0.) -> void:
	action = a
	meal_transfer_started=false
	timer = duration
	waiting_for_view = false
	notes.append(Action.keys()[a])
	print("PENG_TEACH ",Action.keys()[a])

func foot_near_bike() -> Vector3:
	var side := -bike.global_basis.x if lesson.step <= lesson.Step.TO_SHOP else bike.global_basis.x
	return game._grounded(bike.global_position+side*1.02)+Vector3.UP*.035

func box_stance(close_to_opening:=false) -> Vector3:
	var local:=Vector3(.58,0,.83) if close_to_opening else Vector3(.68,0,.52)
	return game._grounded(bike.to_global(local))+Vector3.UP*.025

func work_at_box(point:Vector3,dt:float,loading:bool) -> void:
	var t:=BOX_TIME-timer
	var close_to_opening:bool=t>1.0 and t<(3.37 if loading else 3.49)
	if close_to_opening!=stepped_in:
		stepped_in=close_to_opening
		walker.go(PackedVector3Array([box_stance(stepped_in)]),.035)
	walker.advance(dt,true,false)
	walker.face(point,dt)

func station() -> void:
	walker.dismount(foot_near_bike(),true)
	walker.face(game.actor.body.global_position,1.)
	begin_action(Action.AT_BIKE)

func begin_first_mount() -> void:
	begin_action(Action.BOARD_FIRST,.85)

func begin_shop(resuming := false, shown := false) -> void:
	walker.dismount(foot_near_bike(),resuming)
	if resuming and shown:
		walker.global_position = game._grounded(counter_stance())+Vector3.UP*.02
		walker.face(game.shopkeeper.global_position,1.)
		parcel.show()
		in_hand = true
		walker.begin_carry()
		shop_shown = true
		begin_action(Action.PUPIL_PICKUP)
	else: begin_action(Action.SHOP_EXIT)

func counter_stance() -> Vector3:
	return game.shopkeeper.food_end + game.shopkeeper.global_basis.z*.565 - game.shopkeeper.global_basis.x*.12

func start_second_ride() -> void:
	packed_on_bike = true
	in_hand=false
	parcel.show()
	begin_action(Action.RIDING)
	bike.guide_to(PackedVector3Array(lesson.YARD_PATH))

func begin_yard(resuming := false) -> void:
	walker.dismount(box_stance(),resuming)
	packed_on_bike = true
	begin_action(Action.YARD_EXIT)

func restore_at_door() -> void:
	walker.dismount(game._grounded(Vector3(-53.55,16.45,20.17))+Vector3.UP*.02,true)
	parcel.show()
	parcel.global_position = bag_on_hook(0)
	student_retrieved = true
	door_shown = true
	begin_action(Action.PUPIL_DELIVERS)

func visible_lesson(point: Vector3, distance: float) -> bool:
	var eye: Camera3D=game.actor.camera
	if eye.global_position.distance_to(point)>distance or not eye.is_position_in_frustum(point): return false
	var ray := PhysicsRayQueryParameters3D.create(eye.global_position,point,1)
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.is_empty() or hit.position.distance_to(point)<.25

func observe(point: Vector3, range_m := 5.5) -> bool:
	waiting_for_view = not visible_lesson(point,range_m)
	return not waiting_for_view

func _walk(dt:float) -> bool:
	var gap := walker.global_position.distance_to(game.actor.body.global_position)
	if gap>8.: walking_wait=true
	elif gap<6.: walking_wait=false
	var reached: bool=walker.advance(dt,not walking_wait and not game.riding())
	if walker.blocked_s>3. and not walker.blocked_reported:
		walker.blocked_reported=true
		var contact: Object = walker.get_last_slide_collision().get_collider() if walker.get_last_slide_collision() else null
		lesson.audit.flag("mentor_walk_blocked",{"action":Action.keys()[action],"walk_position":str(walker.global_position),"obstacle":str(contact.get_path()) if contact is Node else ""})
	return reached

func _look_at(point: Vector3,dt: float) -> void:
	walker.advance(dt,false)
	walker.face(point,dt)

func update(dt: float) -> void:
	if transfer_time>=0.: _transfer_pupil(dt)
	if pupil_hang_time>=0.: _hang_pupil(dt)
	match action:
		Action.AT_BIKE: _look_at(game.actor.body.global_position,dt)
		Action.BOARD_FIRST:
			if not walker.mounted:
				if not observe(walker.global_position+Vector3.UP,6.): return
				timer -= dt
				if timer <= 0.: walker.board()
			elif not walker.crossing(): begin_action(Action.RIDING)
		Action.SHOP_EXIT:
			if walker.crossing() or game.riding(): return
			walker.go(PackedVector3Array([Vector3(-27.,12,55.8),Vector3(-25.1,12,57.1),counter_stance()]),.075)
			begin_action(Action.WALK_COUNTER)
		Action.WALK_COUNTER:
			if _walk(dt): begin_action(Action.ORDER,1.1)
		Action.ORDER:
			_look_at(game.shopkeeper.global_position,dt)
			if not observe(walker.global_position+Vector3.UP*1.25): return
			timer-=dt
			if timer<=0.:
				game._say("老彭：老板，取零零一号小面。你对一哈小票，我对一哈门牌。")
				game.shopkeeper.food=parcel
				game.shopkeeper.play_state("serve")
				begin_action(Action.PACK)
		Action.PACK:
			_look_at(game.shopkeeper.global_position,dt)
			if game.shopkeeper.released and not game.shopkeeper.packing and observe(parcel.global_position+Vector3.UP*.23):
				hand_start=walker.grip()
				begin_action(Action.PICK_UP,1.15)
		Action.PICK_UP:
			_look_at(game.shopkeeper.food_end,dt)
			if not observe(game.shopkeeper.food_end+Vector3.UP*.25): return
			timer-=dt
			var goal:Vector3=game.shopkeeper.food_end+Vector3.UP*HANDLE
			walker.shape_right(smoothstep(.47,.98,1.15-timer))
			walker.reach(hand_start.lerp(goal,smoothstep(0.,.80,1.15-timer)),1.)
			if timer<=0.:
				latest_grasp_error=walker.grip().distance_to(goal)
				grasp_angle=walker.finger_bend
				in_hand=true
				hand_start=goal
				begin_action(Action.LIFT_CLEAR,.85)
		Action.LIFT_CLEAR:
			_look_at(game.shopkeeper.food_end,dt)
			if not observe(walker.grip()):return
			timer-=dt
			var t:=.85-timer
			var lift:Vector3=hand_start+Vector3.UP*.16*smoothstep(0.,.42,t)+game.shopkeeper.global_basis.z*.27*smoothstep(.2,.79,t)
			walker.shape_right(1.)
			walker.reach(lift,1.)
			if timer<=0.:
				walker.begin_carry()
				shop_shown=true
				game.shopkeeper.food=game.bag
				walker.reset_reach()
				game._say("老彭：我拿的是零零一号。轮到你了，报零零二号，等店主递给你。")
				begin_action(Action.PUPIL_PICKUP)
				lesson._save()
		Action.PUPIL_PICKUP:
			_look_at(game.shopkeeper.food_end,dt)
			if game.order == game.Order.CARRYING:
				walker.go(PackedVector3Array([Vector3(-25.1,12,57.1),Vector3(-27.,12,55.8),box_stance()]),.075)
				begin_action(Action.RETURN_BIKE)
				lesson._save()
		Action.RETURN_BIKE:
			if _walk(dt):
				hand_start=walker.grip()
				begin_action(Action.LOAD_BOX,BOX_TIME)
		Action.LOAD_BOX:
			var box:Vector3 = bike.to_global(Vector3(0,1.19,.53))
			if not observe(box,7.):return
			work_at_box(box,dt,true)
			if timer==BOX_TIME and not aligned_to_box(box):return
			timer-=dt*.76
			var t:=BOX_TIME-timer
			mentor_box.open(smoothstep(.34,.93,t)*(1.-smoothstep(3.96,4.54,t)))
			if t>1.36 and t<3.29:
				if not meal_transfer_started:
					hand_start=walker.grip()
					meal_transfer_started=true
					walker.carrying=false
				walker.shape_right(1.)
				walker.reach(mentor_box.handle_path(hand_start,smoothstep(1.39,3.14,t),1.),1.)
			elif t>=3.29:
				in_hand=false
				packed_on_bike=true
				walker.shape_right(1.-smoothstep(3.29,3.53,t))
				var clear:Vector3=mentor_box.box.to_global(Vector3(.33,1.36,.58))
				var start:=mentor_box.stored()+Vector3.UP*HANDLE
				var withdrawn:=start.lerp(clear,smoothstep(3.35,3.87,t))
				var rest:Vector3=walker.to_global(Vector3(-.25,.83,.06))
				walker.reach(withdrawn.lerp(rest,smoothstep(3.88,4.44,t)),1.-smoothstep(4.45,4.80,t))
			brace_lid(t)
			if timer<=0.:
				walker.board()
				begin_action(Action.BOARD_AGAIN)
		Action.BOARD_AGAIN:
			if not walker.crossing():
				start_second_ride()
				lesson._change(lesson.Step.TO_YARD,"老彭：我的餐放稳了。把你的袋子放进自己车箱，再骑上来。")
		Action.YARD_EXIT:
			if walker.crossing(): return
			hand_start=walker.grip()
			begin_action(Action.UNLOAD,BOX_TIME)
		Action.UNLOAD:
			var box:Vector3=bike.to_global(Vector3(0,1.16,.53))
			if not observe(box,8.):return
			work_at_box(box,dt,false)
			if timer==BOX_TIME and not aligned_to_box(box):return
			timer-=dt*.76
			var t:=BOX_TIME-timer
			mentor_box.open(smoothstep(.34,.93,t)*(1.-smoothstep(3.96,4.54,t)))
			if t>1.36 and t<2.03:
				if not meal_transfer_started:
					hand_start=walker.grip()
					meal_transfer_started=true
				walker.shape_right(smoothstep(1.58,2.0,t))
				walker.reach(hand_start.lerp(mentor_box.stored()+Vector3.UP*HANDLE,smoothstep(1.38,1.92,t)),smoothstep(1.36,1.57,t))
			elif t>=2.03 and t<3.50:
				in_hand=true;packed_on_bike=false;parcel.show()
				walker.shape_right(1.)
				var carry:Vector3=walker.to_global(Vector3(-.31,.81,.12))
				walker.reach(mentor_box.handle_path(carry,1.-smoothstep(2.03,3.46,t),1.),1.)
			elif t>=3.5 and not walker.carrying:
				walker.reset_reach()
				walker.begin_carry()
			brace_lid(t)
			if timer<=0.:
				begin_action(Action.PUPIL_UNLOAD)
		Action.PUPIL_UNLOAD:
			_look_at(game.actor.body.global_position,dt)
			if student_retrieved and not game.riding():
				walker.go(PackedVector3Array([Vector3(-24.5,14,40),Vector3(-20,14,40),Vector3(-20,15.6,30),Vector3(-18.5,17.2,19.7),Vector3(-49,16.5,19.7),Vector3(-51.2,16.4,19.5),door.point+Vector3(.245,-1.3,-.29)]),.065)
				begin_action(Action.LEAD_HOME)
		Action.LEAD_HOME:
			if _walk(dt):
				hand_start=walker.grip(true)
				begin_action(Action.KNOCK,2.10)
		Action.KNOCK:
			_look_at(door.point-Vector3.BACK*.22,dt)
			if not observe(door.point,5.): return
			timer-=dt
			var t:=2.10-timer
			if knock_index<door.BEATS.size() and t>=door.BEATS[knock_index] and walker.grip(true).distance_to(door.point)>.018:
				t=door.BEATS[knock_index]
				timer=2.10-t
			walker.shape_knock(door.NORMAL,smoothstep(0.,.38,t))
			var goal:=door.point+door.NORMAL*door.clearance(t)
			walker.reach(hand_start.lerp(goal,smoothstep(0.,.48,t)),1.,true)
			var gap:float=(walker.grip(true)-door.point).dot(door.NORMAL)
			if t>.49: peak_retraction=maxf(peak_retraction,gap)
			if knock_index<door.BEATS.size() and t>=door.BEATS[knock_index] and walker.grip(true).distance_to(door.point)<=.018:
				knock_distances.append(walker.grip(true).distance_to(door.point))
				knock_retractions.append(peak_retraction)
				peak_retraction=0.
				door.sound(self,knock_index)
				knock_index+=1
			if timer<=0.:
				walker.reset_reach()
				walker.go(PackedVector3Array([hooks[0]+Vector3(-.17,-1.02,.43)]),.055)
				game._say("老彭：一号的小面到了！　住户：谢谢，两袋都挂门边吧。")
				begin_action(Action.WALK_TO_HOOK)
		Action.WALK_TO_HOOK:
			walker.shape_knock(door.NORMAL,maxf(0.,walker.hand_pose.closure.y-dt*3.))
			if _walk(dt):
				hand_start=walker.grip()
				begin_action(Action.HANG,1.65)
		Action.HANG:
			if not observe(hooks[0],5.): return
			_look_at(hooks[0]-Vector3.RIGHT*.13,dt)
			timer-=dt
			var elapsed:=1.65-timer
			grip_offset=-.024*smoothstep(0.,.62,elapsed)
			walker.reach(hook_path(hand_start,0,elapsed/1.65),1.)
			if timer<=0.:
				latest_hook_error=walker.grip().distance_to(hook_grip(0))
				in_hand=false
				walker.carrying=false
				parcel.rotation=Vector3.ZERO
				parcel.global_position=bag_on_hook(0)
				begin_action(Action.RELEASE_HOOK,.48)
		Action.RELEASE_HOOK:
			_look_at(hooks[0],dt)
			timer-=dt
			var t:=.48-timer
			walker.shape_right(1.-smoothstep(0.,.27,t))
			walker.reach(hook_grip(0)+Vector3(-.015,-.027,.15)*smoothstep(.12,.48,t),1.)
			if timer<=0.:
				walker.reset_reach()
				walker.go(PackedVector3Array([Vector3(-53.3,16.45,19.70),Vector3(-52.35,16.45,20.18)]))
				begin_action(Action.STEP_ASIDE)
		Action.STEP_ASIDE:
			if _walk(dt):
				door_shown=true
				aim_delivery_target()
				game._say("老彭：零零一号挂好了。你也先敲门报单号，再把零零二号挂旁边。")
				begin_action(Action.PUPIL_DELIVERS)
				lesson._save()
		Action.PUPIL_DELIVERS: _look_at(game.actor.body.global_position,dt)

func start_pupil_hang() -> void:
	pupil_hang_start=pupil_grip()
	pupil_hang_time=0.
	if pupil_hand:pupil_hang_ik.start()

func _hang_pupil(dt:float) -> void:
	pupil_hang_time+=dt
	if not student_hooked and not looking_at_fixture(hooks[1]):
		pupil_hang_time=-1.
		pupil_hang_ik.stop()
		return
	var t:=pupil_hang_time
	var grip:=hook_path(pupil_hang_start,1,minf(1.,t/1.65))
	if t>=1.65:
		student_hooked=true
		grip+=Vector3(.01,-.03,.15)*smoothstep(1.67,2.06,t)
		game.bag.global_position=bag_on_hook(1)
		game.bag.rotation=Vector3.ZERO
		game.bag.show()
	if pupil_hand:
		pupil_hang_goal.global_position=grip-(pupil_grip()-pupil_right_wrist)
		pupil_hang_ik.influence=1.-smoothstep(1.85,2.1,t)
	if t>=2.1:
		pupil_hang_time=-1.
		pupil_hang_ik.stop()
		game._deliver()

func bag_on_hook(slot:int) -> Vector3:
	return hooks[slot]-Vector3(.025,HANDLE,0)

func hook_grip(slot:int) -> Vector3:
	return bag_on_hook(slot)+Vector3(-.024,HANDLE,0)

func hook_path(start:Vector3,slot:int,t:float) -> Vector3:
	var grip:=hook_grip(slot)
	var clear:=grip+Vector3(0,.056,.13)
	var above:=grip+Vector3.UP*.056
	if t<.60:return start.lerp(clear,smoothstep(0.,.60,t))
	if t<.81:return clear.lerp(above,smoothstep(.60,.81,t))
	return above.lerp(grip,smoothstep(.81,.96,t))

func aligned_to_box(box:Vector3) -> bool:
	var direction:Vector3=(box-walker.global_position).slide(Vector3.UP).normalized()
	return walker.global_basis.z.dot(direction)>.992

func brace_lid(t:float) -> void:
	var opening:=smoothstep(0.,.32,t)*(1.-smoothstep(.95,1.22,t))
	var closing:=smoothstep(3.56,3.94,t)*(1.-smoothstep(4.54,4.80,t))
	var weight:=maxf(opening,closing)
	walker.hand_pose.closure.y=weight*.62
	if weight<.001:
		walker.arms[1].stop()
		return
	walker._arm(1,mentor_box.lid_edge(1.),weight)

func pupil_grip() -> Vector3:
	return pupil_grasp if pupil_hand else game.actor.body.to_global(Vector3(.28,.86,-.1))

func handle_box(load_food: bool) -> void:
	if transfer_time>=0.: return
	loading_pupil=load_food
	pupil_initial_grip=pupil_grip()
	transfer_time=0.

func _transfer_pupil(dt:float) -> void:
	transfer_time+=dt
	var t:=transfer_time
	pupil_box.open(smoothstep(0.,.38,t)*(1.-smoothstep(1.49,1.90,t)))
	var progress:=smoothstep(.34,1.47,t)
	var start:=pupil_initial_grip if loading_pupil else pupil_grip()
	var side:=signf(game.scooter.to_local(start).x)
	game.bag.show()
	game.bag.global_position=pupil_box.handle_path(start,progress if loading_pupil else 1.-progress,side)-Vector3.UP*HANDLE
	if t>=1.90:
		student_stowed=loading_pupil
		student_retrieved=not loading_pupil
		transfer_time=-1.
		lesson._save()

func _process(dt: float) -> void:
	if pupil_hand:
		var carries:bool=game.order==game.Order.CARRYING and not student_hooked and (not student_stowed or student_retrieved)
		pupil_pose.closure.x=move_toward(pupil_pose.closure.x,float(carries),dt*4.)
		pupil_pose.forward[0]=Vector3.DOWN
		pupil_pose.across[0]=-game.actor.camera.global_basis.z.slide(Vector3.UP).normalized()
	if in_hand:
		var along:Vector3=walker.grip_span
		if Vector2(along.x,along.z).length()>.2:
			var yaw:=atan2(-along.z,along.x)
			# A paper strap has no directional preference. Take the shorter rotation.
			if absf(angle_difference(parcel.rotation.y,yaw))>PI*.5:yaw+=PI
			var target_yaw:=0. if action==Action.HANG else yaw
			parcel.rotation.y=lerp_angle(parcel.rotation.y,target_yaw,1.-exp(-12.*dt))
		var walking:bool=walker.carrying and action in [Action.RETURN_BIKE,Action.LEAD_HOME,Action.WALK_TO_HOOK]
		var tilt:=sin(walker.travelled*4.8)*.045 if walking else 0.
		carry_sway=lerpf(carry_sway,tilt,1.-exp(-6.*dt))
		parcel.rotation.z=carry_sway
		parcel.global_position=walker.grip()-parcel.global_basis*Vector3(grip_offset,HANDLE,0)
	elif packed_on_bike:
		parcel.rotation=Vector3(0,bike.rotation.y,0)
		parcel.global_position=mentor_box.stored()
	if game.order==game.Order.CARRYING and not student_hooked and transfer_time<0.:
		game.bag.show()
		game.bag.global_position=pupil_box.stored() if student_stowed and not student_retrieved else pupil_grip()-Vector3.UP*HANDLE
		game.bag.rotation.y=game.scooter.rotation.y if student_stowed and not student_retrieved else pupil_yaw
		if pupil_hang_time>=0.:
			var align:=smoothstep(0.,.65,pupil_hang_time)
			game.bag.rotation.y=lerp_angle(pupil_yaw,0.,align)
			game.bag.global_position=pupil_grip()-game.bag.global_basis*Vector3(-.024*align,HANDLE,0.)

func hint() -> String:
	var msg := ""
	match action:
		Action.BOARD_FIRST: msg="看老彭上车；随后去骑自己的车"
		Action.SHOP_EXIT,Action.YARD_EXIT: msg="看老彭停车下车；你也刹停、按 P、按 E 下车"
		Action.WALK_COUNTER: msg="跟老彭步行到出餐口"
		Action.ORDER,Action.PACK,Action.PICK_UP,Action.LIFT_CLEAR: msg="到老彭旁边，看他报单号、等餐、提袋"
		Action.RETURN_BIKE,Action.LOAD_BOX,Action.BOARD_AGAIN: msg="提好你的餐，跟老彭回去看他装箱"
		Action.UNLOAD: msg="看老彭从车箱里取出餐袋"
		Action.PUPIL_UNLOAD: msg="轮到你：下车后靠近自己的车箱，按 E 提餐"
		Action.LEAD_HOME: msg="提餐跟老彭上坡，到横巷左转"
		Action.KNOCK,Action.WALK_TO_HOOK,Action.HANG,Action.RELEASE_HOOK,Action.STEP_ASIDE: msg="跟到门前，看老彭敲门、报号、挂餐"
	if msg.is_empty(): return msg
	if waiting_for_view: return msg+"\n靠近些，转头看老彭手边"
	if walking_wait: return msg+"\n老彭停下来等你了"
	return msg
