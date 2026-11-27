extends Node3D

enum Step { CHECK_IN, MOUNT, TO_SHOP, SHOP, TO_YARD, LAST_METRES, DONE, RETURN }
const Unit = preload("res://scripts/unit_interior.gd")
const GUIDE = preload("res://scripts/mentor_scooter.gd")
const RECORD := "user://first_shift_v1.cfg"
const STATION := Vector3(-50,11.8,52)
const STUDENT_BIKE := Vector3(-54.5,11.8,52)
const SHOP_STOP := Vector3(-29.3,11.8,55.2)
const YARD_STOP := Vector3(-48.7,16.4,19.6)
const SHOP_PATH := [Vector3(-39,12,52),SHOP_STOP]
const YARD_PATH := [Vector3(-26,11.9,54.7),Vector3(-24.7,12.3,52),Vector3(-25.3,12.7,48),Vector3(-24.6,14,40.5),Vector3(-26.0,14.65,35),Vector3(-26.0,15.5,29),Vector3(-25.6,16.2,24),Vector3(-24.6,16.6,22),Vector3(-28,16.8,19.7),YARD_STOP]
const STATION_STOP := Vector3(-44.5,11.8,54.4)
const COURT_STOP := Vector3(-34,16.5,20.8)
const STATION_ROUTE := [Vector3(-26.4,12,54.8),Vector3(-26.6,12,51.8),Vector3(-30,12,51.6),Vector3(-37,12,53),STATION_STOP]
const ORDER_NAMES := ["小院一单元 201","骑手站取餐架","篮球场下巷取餐架"]
var round_index := 0
var shelves:Array[Node3D]=[]
var chosen_slot := -1
var recipient_answered:=false
var return_boarded := false
var dispatch_deliveries := 0
var dispatch_leg := 0

func outgoing(index:int) -> PackedVector3Array:
	if index==1:return PackedVector3Array(STATION_ROUTE)
	var path:=PackedVector3Array(YARD_PATH)
	if index==2:path[-1]=COURT_STOP
	return path

func returning(index:int) -> PackedVector3Array:
	if index==1:return PackedVector3Array([Vector3(-47,12,54),Vector3(-48,12,51.6),Vector3(-44.8,12,50.4),Vector3(-37,12,52.2),SHOP_STOP])
	# Use the open downhill forecourt for the U-turn while the second bike
	# is still pulling out of its bay at the door.
	return PackedVector3Array([
		Vector3(-50.7,16,20.9),Vector3(-51.1,15.7,23.6),Vector3(-49.6,15.3,25.9),
		Vector3(-45.7,15.4,26.8),Vector3(-37,15.6,25.8),Vector3(-29.8,16,24.7),
		Vector3(-26.7,16,25.5),Vector3(-26,15.5,29),Vector3(-26,14.7,35),
		Vector3(-24.6,14,40.5),Vector3(-25.3,12.7,48),Vector3(-24.7,12.3,52),
		Vector3(-26,11.9,54.7),Vector3(-27.5,12,52.2),Vector3(-32.7,12,52.1),
		Vector3(-33.6,12,54.6),SHOP_STOP])

func after_shift_return() -> PackedVector3Array:
	if dispatch_deliveries>0:return returning(1)
	# The pupil normally parks east of the court rack. Turn downhill on the
	# open side of that bay, then approach the shop in a single forward arc.
	return PackedVector3Array([
		Vector3(-36.8,16.2,22.6),Vector3(-37.2,15.9,24.8),Vector3(-35.0,15.8,26),
		Vector3(-30.7,16,24.6),Vector3(-27.4,16,24.6),Vector3(-26.0,15.5,29.0),
		Vector3(-26,14.7,35),Vector3(-24.6,14,40.5),Vector3(-25.3,12.7,48),
		Vector3(-24.8,12.3,51.8),Vector3(-25.3,11.9,54.5),Vector3(-27.1,11.8,55.9),SHOP_STOP])

func receipt(mentor_order:=false) -> int:
	return round_index*2+(1 if mentor_order else 2)

func collection() -> Node3D:
	return shelves[round_index-1]

func release_spot(index:int) -> Vector3:
	return [YARD_STOP,STATION_STOP,COURT_STOP][index]

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
	if checkpoint==RECORD and "--practice-unit" in OS.get_cmdline_user_args():
		record_path=""
		step=Step.LAST_METRES
	var practice_lunch:=checkpoint==RECORD and "--practice-lunch" in OS.get_cmdline_user_args()
	var practice_passage:=checkpoint==RECORD and "--practice-passage" in OS.get_cmdline_user_args()
	if practice_lunch or practice_passage:
		record_path=""
		step=Step.DONE
		round_index=2
		game.delivered_count=3
		game.earnings=24
	var record := ConfigFile.new()
	if not record_path.is_empty() and record.load(record_path) == OK:
		player_bike.tyre_pressure=clampf(float(record.get_value("shift","tyre_pressure",player_bike.FULL_PRESSURE)),1.1,player_bike.FULL_PRESSURE)
		step = clampi(int(record.get_value("shift","step",0)),Step.CHECK_IN,Step.RETURN)
		game.delivered_count = maxi(0,int(record.get_value("shift","deliveries",0)))
		round_index=clampi(int(record.get_value("shift","round",0)),0,2)
		if step==Step.DONE and not record.has_section_key("shift","round"):
			round_index=1
			step=Step.RETURN
		if game.shancheng:
			game.shancheng.stage=clampi(int(record.get_value("shancheng","stage",0)),0,2)
			game.shancheng.rest_parcel()
		if game.riverside_tea:
			game.riverside_tea.stage=clampi(int(record.get_value("riverside_tea","stage",0)),0,2)
			game.riverside_tea.rest_parcel()
		game.earnings = maxi(0,int(record.get_value("shift","earnings",0)))
	game.owner_scene.hud.theme.default_font = preload("res://assets/fonts/first_shift.otf")
	game.owner_scene.objective_label.add_theme_font_size_override("font_size",21)
	game.owner_scene.controls_label.add_theme_font_size_override("font_size",17)
	game.owner_scene.get_window().title += " · 穿楼托送" if practice_passage else (" · 午市拼送练习" if practice_lunch else " · 入职教学")
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
	for index in 2:
		var site:=preload("res://scripts/shift_collection_shelf.gd").new()
		add_child(site)
		var anchor:Vector3=[Vector3(-47.5,11.95,50.8),Vector3(-37.6,16.6,18.5)][index]
		site.install(self,anchor,ORDER_NAMES[index+1],index+1)
		shelves.append(site)
	if round_index>0 and step!=Step.DONE:
		demo.reset_order()
		game.bag.write_ticket(receipt(),round_index==1)
	if step==Step.DONE:
		_place_vehicle(mentor,SHOP_STOP,PI/2)
		_place_vehicle(player_bike,record.get_value("shift","pupil_stop",COURT_STOP+Vector3(4,0,0)),record.get_value("shift","pupil_yaw",PI/2))
		_walk_from(player_bike.global_position+player_bike.global_basis.x*1.35,player_bike.global_position)
		game.order=game.Order.DELIVERED
		mentor.escort=false
		return_boarded=true
		unlock_free_play()
		if practice_lunch:
			# Park facing uphill, outside the instructor's independent return arc.
			_place_vehicle(player_bike,Vector3(-25.25,12.55,50.5),0.)
			_walk_from(game.owner_scene._pickup+Vector3(.7,0,-.2),game.shop.global_position)
		game.lunch.restore(record)
		game.passage.restore(record)
		if game.shancheng and game.shancheng.stage==game.shancheng.Stage.CARRYING:
			var approach: Array=game.shancheng.stops[0].approach
			_walk_from(Vector3(approach[0],approach[2],-approach[1]),game.shancheng.sender.global_position)
		elif game.riverside_tea and game.riverside_tea.stage==game.riverside_tea.Stage.CARRYING:
			var approach: Array=game.riverside_tea.stops[0].approach
			_walk_from(Vector3(approach[0],approach[2],-approach[1]),game.riverside_tea.sender.global_position)
		if practice_passage:
			_place_vehicle(player_bike,YARD_STOP+Vector3(3.6,0,0),PI/2)
			_walk_from(Unit.COURT+Vector3(1.2,0,0),Vector3(-54.9,17.8,19.5))
			game.passage.begin()
		demo.start_dispatch_pickup()
		return
	if step==Step.RETURN or (step==Step.TO_SHOP and round_index>0):
		var previous:=maxi(0,round_index-1)
		var stand:=release_spot(previous)
		_place_vehicle(mentor,record.get_value("shift","guide_stop",stand),record.get_value("shift","guide_yaw",PI/2))
		_place_vehicle(player_bike,record.get_value("shift","pupil_stop",stand+Vector3(3.6,0,0)),record.get_value("shift","pupil_yaw",PI/2))
		_walk_from(stand+Vector3(1.2,0,1.9),mentor.global_position)
		demo.walker.dismount(game._grounded(mentor.global_position+Vector3(0,0,1.4)),true)
		game.order=game.Order.DELIVERED
		step=Step.RETURN
		begin_return(false)
		return
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
		var stop:=release_spot(round_index)
		_place_vehicle(mentor,record.get_value("shift","guide_stop",stop),record.get_value("shift","guide_yaw",PI/2))
		_place_vehicle(player_bike,record.get_value("shift","pupil_stop",stop+Vector3(3.6,0,0)),record.get_value("shift","pupil_yaw",PI/2))
		_walk_from(player_bike.global_position+Vector3(0,0,1.3),mentor.global_position+Vector3.UP)
		game.order = game.Order.CARRYING
		game.owner_scene._delivery_stage = 1
		demo.student_stowed = true
		if round_index==0 and record.get_value("shift","door_shown",false):
			_walk_from(Unit.LANDING,demo.door.point)
			demo.restore_at_door()
			demo.student_knocked = record.get_value("shift","knocked",record.get_value("shift","rang",false))
			demo.aim_delivery_target()
		elif round_index>0 and record.get_value("shift","door_shown",false):
			var shelf:=collection()
			demo.walker.dismount(game._grounded(shelf.to_global(Vector3(-1.2,0,.85))),true)
			demo.parcel.show()
			demo.parcel.global_position=shelf.slots[0]
			demo.student_retrieved=true
			demo.student_stowed=false
			demo.door_shown=true
			recipient_answered=record.get_value("shift","answered",false)
			_walk_from(shelf.to_global(Vector3(0,0,1.2)),shelf.slots[1])
			demo.begin_action(demo.Action.PUPIL_SHELF)
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
	record.set_value("shift","round",round_index)
	record.set_value("shift","answered",recipient_answered)
	if mentor:
		record.set_value("shift","guide_stop",mentor.global_position)
		record.set_value("shift","guide_yaw",mentor.rotation.y)
		record.set_value("shift","pupil_stop",player_bike.global_position)
		record.set_value("shift","pupil_yaw",player_bike.rotation.y)
		record.set_value("shift","tyre_pressure",player_bike.tyre_pressure)
	record.set_value("shift","deliveries",game.delivered_count)
	record.set_value("shift","earnings",game.earnings)
	if demo:
		record.set_value("shift","shop_shown",demo.shop_shown)
		record.set_value("shift","has_food",game.order==game.Order.CARRYING)
		record.set_value("shift","stowed",demo.student_stowed)
		record.set_value("shift","door_shown",demo.door_shown)
		record.set_value("shift","knocked",demo.student_knocked)
	if game.lunch:game.lunch.store_progress(record)
	if game.shancheng:record.set_value("shancheng","stage",game.shancheng.stage)
	if game.riverside_tea:record.set_value("riverside_tea","stage",game.riverside_tea.stage)
	if game.passage:game.passage.save_to(record)
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
	return step in [Step.DONE,Step.RETURN] or (demo and demo.transfer_time<0. and (demo.action == demo.Action.RIDING or demo.action == demo.Action.PUPIL_UNLOAD))

func can_deliver() -> bool:
	return step == Step.DONE or (step == Step.LAST_METRES and demo and demo.door_shown)

func vehicle_prompt() -> String:
	if step == Step.TO_YARD and not demo.student_stowed: return "把 %03d 号放进自己的车箱" % receipt()
	if step == Step.LAST_METRES: return "从车箱取出 %03d 号" % receipt()
	return "骑电瓶车"

func use_bike() -> void:
	if step == Step.TO_YARD and not demo.student_stowed:
		demo.handle_box(true)
		game._say("%03d 号装好了，再按 E 上车。" % receipt())
		_save()
	elif step == Step.LAST_METRES and demo.action==demo.Action.PUPIL_UNLOAD:
		demo.handle_box(false)
		game._say("提稳餐袋，跟上老彭。")
	else: player_bike.enter(game.actor)

func delivery_prompt() -> String:
	if step == Step.DONE: return game.free_delivery_prompt()
	if round_index>0:return "对照小票，放到乙位"
	return "把零零二号挂在第二个钩上" if demo.student_knocked else "敲门，报零零二号"

func student_handover() -> bool:
	if step == Step.DONE: return game.free_handover()
	if round_index>0:return can_deliver() and chosen_slot==1 and demo.student_hooked
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
	if step in [Step.RETURN,Step.DONE]:
		update_return(delta)
		return
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
				_change(Step.LAST_METRES,"老彭：%s到了。靠边停稳，跟我取餐交付。" % ORDER_NAMES[round_index])

func notify_recipient() -> void:
	if round_index!=2 or step!=Step.LAST_METRES or not demo.door_shown or recipient_answered:return
	recipient_answered=true
	game.play_door_chime(collection().call_point)
	game._say("球友：006 号是我的，麻烦放乙位。")
	_save()

func place_on_shelf(slot:int) -> void:
	if not can_deliver() or round_index==0 or game.order!=game.Order.CARRYING:return
	if round_index==2 and not recipient_answered:return
	if slot!=1:
		game._say("看袋上的小票，你的收餐位是乙。")
		return
	if chosen_slot>=0:return
	if not facing_shelf():
		game._say("走到乙位前面，看着架面再放下。")
		return
	chosen_slot=slot
	demo.begin_shelf_handover()

func facing_shelf() -> bool:
	var shelf:=collection()
	var point:Vector3=shelf.slots[1]
	var camera:Camera3D=game.actor.camera
	return game.manager.reachable(shelf.bay_targets[1]) and (-camera.global_basis.z).dot(camera.global_position.direction_to(point))>.72

func begin_return(solo:bool) -> void:
	return_boarded=false
	mentor.escort=not solo
	demo.begin_action(demo.Action.BACK_TO_SADDLE)
	var route:=PackedVector3Array([demo.box_stance()])
	if round_index==1 and not solo and demo.walker.global_position.y>Unit.LANDING.y-.6:
		route=Unit.downstairs(demo.box_stance())
	demo.walker.go(route,.16)

func unlock_free_play() -> void:
	if not game.lunch:
		game.lunch=preload("res://scripts/lunch_run.gd").new()
		game.add_child(game.lunch)
		game.lunch.setup(game,shelves[1])
		game.passage=preload("res://scripts/passage_order.gd").new()
		game.add_child(game.passage)
		game.passage.setup(game)
	game.select_free_address()
	game.actor.review_shortcuts=true
	game.owner_scene.view_picker.get_parent().show()
	game.owner_scene._mode_changed(game.actor.walking)
	sign.visible=false

func update_return(dt:float) -> void:
	var solo:=step==Step.DONE
	if not return_boarded:
		sign.global_position=demo.walker.global_position+Vector3.UP*1.98
		if not demo.walker.mounted:
			if demo.walker.advance(dt,true):demo.walker.board()
			return
		if demo.walker.crossing():return
		return_boarded=true
		demo.begin_action(demo.Action.RIDING)
		mentor.guide_to(after_shift_return() if solo else returning(round_index-1))
		if not solo:
			demo.reset_order()
			_change(Step.TO_SHOP,"老彭：回面馆接下一单。上车跟我走。")
		return
	if solo:
		if demo.action!=demo.Action.RIDING:
			demo.update(dt)
		elif mentor.arrived:
			if demo.packed_on_bike:demo.begin_yard()
			else:demo.start_dispatch_pickup()

func delivery_finished() -> void:
	if step==Step.LAST_METRES:
		if round_index<2:
			round_index+=1
			_change(Step.RETURN,["","老彭：第一单结了。回面馆接骑手站的单，这单辣子另装。","老彭：最后一趟到球场下巷。看小票分清甲乙收餐位。"][round_index])
			begin_return(false)
		else:
			_change(Step.DONE,"老彭：今天三单都送齐了。我回站跑下一趟，你可以自己接单了。")
			begin_return(true)
			unlock_free_play()
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
	if step==Step.RETURN:return "第 %d / 3 单 · %s\n跟老彭回到各自的车旁，骑回面馆接单" % [round_index+1,ORDER_NAMES[round_index]]
	if demo and step != Step.DONE:
		var hint: String = demo.hint()
		if not hint.is_empty(): return "第 %d / 3 单 · %s\n"%[round_index+1,ORDER_NAMES[round_index]]+hint
		if step == Step.TO_YARD and not demo.student_stowed: return "第一天 · 跟着装餐\n靠近自己的车按 E 装箱，再上车"
	match step:
		Step.CHECK_IN: return "第一天 · 到岗报到\n走近老彭，按 E 报到"
		Step.MOUNT: return "第一天 · 骑上自己的电瓶车\n车在老彭身后 %d 米，靠近按 E" % _distance(player_bike.global_position)
		Step.SHOP:
			match game.order:
				game.Order.PREPARING: return "第一天 · 在出餐口等候\n店主正在打包你的小面"
				game.Order.READY: return "第 %d 单 · %s\n%s"%[round_index+1,ORDER_NAMES[round_index],"按 E 把辣子单独装好，再提餐" if game.condiments.state==game.condiments.State.ON_COUNTER else "在出餐口按 E 提餐"]
				_: return "第 %d / 3 单 · %s\n%s"%[round_index+1,ORDER_NAMES[round_index],"餐已拿好，跟老彭回车边" if game.order==game.Order.CARRYING else "到梯坎小面出餐口按 E · %d 米"%_distance(game.shop.global_position)]
		Step.LAST_METRES: return "第一天 · 轮到你交付\n走到 201 户门前按 E，"+("把你的餐袋挂好" if demo.student_knocked else "敲门报单号")
		Step.DONE: return "第一天教学完成 · 已学会取送餐\n累计 %d 单 · %d 元，面馆可接午市拼送" % [game.delivered_count,game.earnings]
	var destination:String = "梯坎小面" if step == Step.TO_SHOP else ORDER_NAMES[round_index]
	if audit.active_stall >= 0:
		return "老彭在%s途中遇阻\n给车头留点空间，等路通再跟上" % destination
	if mentor.arrived:
		return "老彭已到%s · 距你 %d 米\n停在他附近，空格刹停，P 停车，E 下车" % [destination,_distance(mentor.global_position)]
	if not game.riding(): return "第一天 · 骑车跟老彭去%s\n回到自己的车旁按 E · %d 米" % [destination,_distance(player_bike.global_position)]
	if mentor.waiting: return "老彭在你%s等你 · %d 米\n骑近他就会继续带路" % [_bearing(mentor.global_position),_distance(mentor.global_position)]
	return "第一天 · 跟车到%s\n老彭在你%s · %d 米" % [destination,_bearing(mentor.global_position),_distance(mentor.global_position)]
