extends Node3D

enum Step { CHECK_IN, MOUNT, TO_SHOP, SHOP, TO_YARD, LAST_METRES, DONE }
const GUIDE = preload("res://scripts/mentor_scooter.gd")
const RECORD := "user://first_shift_v1.cfg"
const STATION := Vector3(-50,11.8,52)
const STUDENT_BIKE := Vector3(-54.5,11.8,52)
const SHOP_STOP := Vector3(-29.3,11.8,55.2)
const YARD_STOP := Vector3(-25.4,14.4,36)
const SHOP_PATH := [Vector3(-39,12,52),SHOP_STOP]
const YARD_PATH := [Vector3(-26,11.9,54.7),Vector3(-24.7,12.3,52),Vector3(-25.3,12.7,48),YARD_STOP]
var game: Node3D
var mentor: CharacterBody3D
var audit: Node
var sign: Label3D
var step := Step.CHECK_IN
var record_path := RECORD
var pupil_knock_time := -1.
var pupil_beat := 0
var player_bike: CharacterBody3D
var demo: Node3D

func setup(world: Node3D, checkpoint: String = RECORD) -> void:
	record_path = checkpoint
	game = world
	player_bike = game.scooter
	if checkpoint == RECORD and ("--practice-day-one" in OS.get_cmdline_user_args() or "--day-one-test" in OS.get_cmdline_user_args()):
		record_path = ""
	var record := ConfigFile.new()
	if not record_path.is_empty() and record.load(record_path) == OK:
		step = clampi(int(record.get_value("shift","step",0)),Step.CHECK_IN,Step.DONE)
		game.delivered_count = maxi(0,int(record.get_value("shift","deliveries",0)))
		game.earnings = maxi(0,int(record.get_value("shift","earnings",0)))
	game.owner_scene.hud.theme.default_font = preload("res://assets/fonts/first_shift.otf")
	game.owner_scene.objective_label.add_theme_font_size_override("font_size",21)
	game.owner_scene.controls_label.add_theme_font_size_override("font_size",17)
	game.owner_scene.get_window().title += " · 入职教学"
	if step == Step.DONE:
		_walk_from(Vector3(-22.4,11.5,59),game.shop.global_position)
		game.order = game.Order.DELIVERED
		return
	game.actor.review_shortcuts = false
	game.owner_scene.view_picker.get_parent().hide()
	mentor = GUIDE.new()
	mentor.name = "LaoPeng"
	add_child(mentor)
	mentor.learner = player_bike
	audit = preload("res://scripts/mentor_route_audit.gd").new()
	add_child(audit)
	var issue_file := ""
	if record_path == RECORD:
		issue_file = "user://route_issues/first_shift_%d_%d.json" % [int(Time.get_unix_time_from_system()),OS.get_process_id()]
	audit.setup(self,issue_file)
	mentor.collision_mask |= player_bike.collision_mask
	player_bike.collision_mask |= GUIDE.GUIDE_LAYER
	game.actor.walk_collision_mask |= GUIDE.GUIDE_LAYER
	var target: Node3D = game._target("mentor.check_in",Vector3.ZERO,func(): return "向老彭报到",func(): return step == Step.CHECK_IN,_check_in,mentor)
	target.position = Vector3.UP
	target.radius = 2.65
	sign = game._add_marker(target,"老彭",Color("f2c27c"))
	sign.font = game.owner_scene.hud.theme.default_font
	sign.position.y = .98
	for marker: Label3D in [sign,game.vehicle_marker,game.shop_marker,game.door_marker]:
		marker.fixed_size = true
		marker.pixel_size = .0011
	demo = preload("res://scripts/mentor_demonstration.gd").new()
	add_child(demo)
	demo.setup(self)
	if step <= Step.TO_SHOP:
		if step == Step.TO_SHOP: step = Step.MOUNT
		_place_vehicle(mentor,STATION,-PI/2)
		_place_vehicle(player_bike,STUDENT_BIKE,-PI/2)
		_walk_from(Vector3(-49.2,12.1,49.8),mentor.global_position+Vector3.UP*1.25)
		demo.station()
		if step == Step.MOUNT: demo.begin_first_mount()
	elif step <= Step.TO_YARD:
		_place_vehicle(mentor,SHOP_STOP,-PI/2)
		_place_vehicle(player_bike,SHOP_STOP+Vector3(-3.4,0,.25),-PI/2)
		_walk_from(game.owner_scene._pickup + Vector3(.85,0,-.2),game.shop.global_position)
		if step == Step.TO_YARD:
			game.order = game.Order.CARRYING
			game.owner_scene._delivery_stage = 1
			demo.student_stowed = record.get_value("shift","stowed",true)
			demo.start_second_ride()
		else:
			demo.begin_shop(true,record.get_value("shift","shop_shown",false))
			if record.get_value("shift","has_food",false):
				game.order = game.Order.CARRYING
				game.owner_scene._delivery_stage = 1
	else:
		_place_vehicle(mentor,YARD_STOP,0.)
		_place_vehicle(player_bike,YARD_STOP+Vector3(0,0,3.6),0.)
		_walk_from(YARD_STOP+Vector3(1.4,0,3.6),game.destination.global_position)
		game.order = game.Order.CARRYING
		game.owner_scene._delivery_stage = 1
		demo.student_stowed = true
		if record.get_value("shift","door_shown",false):
			_walk_from(game.owner_scene._dropoff+Vector3(1.2,0,.15),game.destination.global_position)
			demo.restore_at_door()
			demo.student_knocked = record.get_value("shift","knocked",record.get_value("shift","rang",false))
			demo.aim_delivery_target()
		else: demo.begin_yard(true)

func _place_vehicle(vehicle: CharacterBody3D, anchor: Vector3, yaw: float) -> void:
	vehicle.global_position = game._grounded(anchor) + Vector3.UP*.04
	vehicle.rotation.y = yaw
	vehicle.safe_park_position = vehicle.global_position

func _walk_from(anchor: Vector3, look: Vector3) -> void:
	game.actor.set_walk_origin(game._grounded(anchor)+Vector3.UP*.04,look)

func _save() -> void:
	if record_path.is_empty(): return
	var record := ConfigFile.new()
	record.set_value("shift","step",step)
	record.set_value("shift","deliveries",game.delivered_count)
	record.set_value("shift","earnings",game.earnings)
	if demo:
		record.set_value("shift","shop_shown",demo.shop_shown)
		record.set_value("shift","has_food",game.order==game.Order.CARRYING)
		record.set_value("shift","stowed",demo.student_stowed)
		record.set_value("shift","door_shown",demo.door_shown)
		record.set_value("shift","knocked",demo.student_knocked)
	var temp := record_path+".%d.tmp" % OS.get_process_id()
	var err := record.save(temp)
	if err == OK:
		err = DirAccess.rename_absolute(ProjectSettings.globalize_path(temp),ProjectSettings.globalize_path(record_path))
	if err != OK: push_warning("First shift checkpoint: "+error_string(err))

func _change(next: Step, line: String) -> void:
	step = next
	game._say(line)
	game.toast_time = 5.
	_save()

func _check_in() -> void:
	if step == Step.CHECK_IN:
		demo.begin_first_mount()
		_change(Step.MOUNT,"老彭：名字我记了。后头那辆是你的，骑上来，跟到我的黄帽子走。")

func can_order() -> bool:
	return step == Step.DONE or (step == Step.SHOP and demo and demo.shop_shown)

func can_mount() -> bool:
	return step == Step.DONE or (demo and demo.transfer_time<0. and (demo.action == demo.Action.RIDING or demo.action == demo.Action.PUPIL_UNLOAD))

func can_deliver() -> bool:
	return step == Step.DONE or (step == Step.LAST_METRES and demo and demo.door_shown)

func vehicle_prompt() -> String:
	if step == Step.TO_YARD and not demo.student_stowed: return "把零零二号放进自己的车箱"
	if step == Step.LAST_METRES: return "从车箱取出零零二号"
	return "骑电瓶车"

func use_bike() -> void:
	if step == Step.TO_YARD and not demo.student_stowed:
		demo.handle_box(true)
		game._say("零零二号装好了，再按 E 上车。")
		_save()
	elif step == Step.LAST_METRES and demo.action==demo.Action.PUPIL_UNLOAD:
		demo.handle_box(false)
		game._say("提稳餐袋，跟上老彭。")
	else: player_bike.enter(game.actor)

func delivery_prompt() -> String:
	if step == Step.DONE: return "交付餐食"
	return "把零零二号挂在第二个钩上" if demo.student_knocked else "敲门，报零零二号"

func student_handover() -> bool:
	if step == Step.DONE: return true
	if not can_deliver(): return false
	if pupil_knock_time>=0. or demo.pupil_hang_time>=0.: return false
	if demo.student_hooked:return true
	if not demo.student_knocked:
		if not demo.looking_at_fixture(demo.door.point):
			game._say("走近木门，看着门板再敲。")
			return false
		pupil_knock_time=0.
		pupil_beat=0
		demo.pupil_strikes.clear()
		return false
	if not demo.looking_at_fixture(demo.hooks[1]):return false
	demo.start_pupil_hang()
	return false

func uses_hud() -> bool:
	return step != Step.DONE or game.order == game.Order.DELIVERED

func _near_instructor_stop() -> bool:
	return mentor.arrived and player_bike.global_position.distance_to(mentor.global_position)<8. and demo.visible_lesson(mentor.global_position+Vector3.UP,10.)

func _physics_process(delta: float) -> void:
	if not demo: return
	if step == Step.DONE: return
	demo.update(delta)
	if pupil_knock_time>=0.:
		if not demo.looking_at_fixture(demo.door.point):
			pupil_knock_time=-1.
			demo.animate_pupil_knock(-1.)
		else:
			pupil_knock_time+=delta
			demo.animate_pupil_knock(pupil_knock_time)
			if pupil_beat<3 and pupil_knock_time>=demo.door.BEATS[pupil_beat]:
				demo.pupil_strikes.append(demo.pupil_knuckle.distance_to(demo.door.point))
				demo.door.sound(demo,pupil_beat)
				pupil_beat+=1
			if pupil_knock_time>=2.10:
				pupil_knock_time=-1.
				demo.animate_pupil_knock(-1.)
				demo.student_knocked=true
				demo.aim_delivery_target()
				game._say("住户：零零二号也到了？好，挂旁边就行。")
				_save()
	sign.global_position = (mentor.global_position if demo.walker.mounted else demo.walker.global_position)+Vector3.UP*1.98
	match step:
		Step.MOUNT:
			if game.riding():
				mentor.guide_to(PackedVector3Array(SHOP_PATH))
				_change(Step.TO_SHOP,"老彭：跟到我后头。前面梯坎小面，第一单从那里取。")
		Step.TO_SHOP:
			if _near_instructor_stop():
				demo.begin_shop()
				_change(Step.SHOP,"老彭：到了，看我先停、下车。跟我去出餐口。")
		Step.TO_YARD:
			if _near_instructor_stop():
				demo.begin_yard()
				_change(Step.LAST_METRES,"老彭：前面要走路。我先停车提餐，跟我上去。")

func delivery_finished() -> void:
	if step == Step.LAST_METRES:
		step = Step.DONE
		game.destination.global_position=demo.old_target
		game.destination.radius=demo.old_radius
		game.actor.review_shortcuts = true
		game.owner_scene.view_picker.get_parent().show()
		game.owner_scene._mode_changed(game.actor.walking)
		if is_instance_valid(sign): sign.visible = false
	_save()

func _distance(point: Vector3) -> int:
	return roundi(game.actor.body.global_position.distance_to(point))

func controls() -> String:
	if game.riding():
		return "W 加速　S 减速或倒车　A / D 转向　空格刹车\n车停稳后按 P 停车，再按 E 下车"
	return "W A S D 走路　移动鼠标转头　E 交互\nEsc 释放鼠标　单击场景继续"

func _bearing(point: Vector3) -> String:
	var direction: Vector3 = game.actor.camera.to_local(point)
	if absf(direction.x) > absf(direction.z):
		return "右边" if direction.x > 0 else "左边"
	return "身后" if direction.z > 0 else "前方"

func objective() -> String:
	if demo and step != Step.DONE:
		var hint: String = demo.hint()
		if not hint.is_empty(): return "第一天 · 跟老彭学送单\n"+hint
		if step == Step.TO_YARD and not demo.student_stowed: return "第一天 · 跟着装餐\n靠近自己的车按 E 装箱，再上车"
	match step:
		Step.CHECK_IN: return "第一天 · 到岗报到\n走近老彭，按 E 报到"
		Step.MOUNT: return "第一天 · 骑上自己的电瓶车\n车在老彭身后 %d 米，靠近按 E" % _distance(player_bike.global_position)
		Step.SHOP:
			match game.order:
				game.Order.PREPARING: return "第一天 · 在出餐口等候\n店主正在打包你的小面"
				game.Order.READY: return "第一天 · 拿好小院一号的餐\n在出餐口按 E 领取"
				_: return "第一天 · 到梯坎小面取单\n走到店主身边按 E · %d 米" % _distance(game.shop.global_position)
		Step.LAST_METRES: return "第一天 · 轮到你交付\n走到一号门前按 E，"+("把你的餐袋挂好" if demo.student_knocked else "敲门报单号")
		Step.DONE: return "第一天教学完成 · 已学会取送餐\n累计 %d 单 · %d 元，可回面馆接单" % [game.delivered_count,game.earnings]
	var destination := "梯坎小面" if step == Step.TO_SHOP else "小院坡口"
	if audit.active_stall >= 0:
		return "老彭在%s途中遇阻\n给车头留点空间，等路通再跟上" % destination
	if mentor.arrived:
		return "老彭已到%s · 距你 %d 米\n停在他附近，空格刹停，P 停车，E 下车" % [destination,_distance(mentor.global_position)]
	if not game.riding(): return "第一天 · 骑车跟老彭去%s\n回到自己的车旁按 E · %d 米" % [destination,_distance(player_bike.global_position)]
	if mentor.waiting: return "老彭在你%s等你 · %d 米\n骑近他就会继续带路" % [_bearing(mentor.global_position),_distance(mentor.global_position)]
	return "第一天 · 跟车到%s\n老彭在你%s · %d 米" % [destination,_bearing(mentor.global_position),_distance(mentor.global_position)]
