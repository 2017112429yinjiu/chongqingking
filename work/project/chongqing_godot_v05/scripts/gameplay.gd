extends Node3D
const Unit = preload("res://scripts/unit_interior.gd")
var free_flat:=0
var free_answered:=false
var shelf_time:=-1.0
var shelf_start:=Vector3.ZERO
var shelf_yaw:=0.0
var shancheng: Node3D
var riverside_tea: Node3D
var outer_market_handoff: Node3D
var passage: Node3D
var lunch: Node3D
var free_wrist:BoneAttachment3D
const Target = preload("res://scripts/interaction_target.gd")
const Manager = preload("res://scripts/interaction_manager.gd")
const Scooter = preload("res://scripts/scooter_controller.gd")
enum Order { AVAILABLE, PREPARING, READY, CARRYING, DELIVERED }
var order: int = Order.AVAILABLE
var preparation: float = 0.0
var delivered_count: int = 0
var earnings: int = 0
var manager: Node
var lesson: Node3D
var scooter: CharacterBody3D
var actor: Node3D
var shop: Node3D
var destination: Node3D
var bag: Node3D
var shopkeeper: Node3D
var condiments:=preload("res://scripts/counter_condiments.gd").new()
var owner_scene: Node3D
var toast: String = ""
var toast_time: float = 0.0
var shop_marker: Label3D
var door_marker: Label3D
var vehicle_marker: Label3D
var next_notice: int = 0
var rinse_tap: Node3D
var court_resident: Node3D
const RESIDENT_NOTICES = [
	"清掏水沟　周四上午九点，从下巷口开始清理。请收好花盆，留出通道。",
	"修伞 · 换拉链　逢二、五下午，师傅在石梯转角的屋檐下出摊。",
	"借竹篮　菜场的蓝绳竹篮已洗净，放在门房。取用请记得归还。"
]

func public_handoff_in_progress() -> bool:
	for handoff: Node3D in [shancheng,riverside_tea,outer_market_handoff]:
		if handoff and handoff.stage==handoff.Stage.CARRYING:
			return true
	return false

func setup(main: Node3D) -> void:
	owner_scene = main
	actor = main.explorer
	manager = Manager.new()
	manager.actor = actor
	add_child(manager)
	shop = _target("shop.noodle",main._pickup+Vector3.UP,func(): return _shop_prompt(),func(): return not public_handoff_in_progress() and (not passage or passage.stage==passage.Stage.IDLE) and ((lunch and lunch.active) or (order != Order.CARRYING and (not lesson or lesson.can_order()))),func(): _shop_action())
	destination = _target("delivery.home",main._dropoff+Vector3.UP,func(): return lesson.delivery_prompt() if lesson else free_delivery_prompt(),func(): return (not lunch or not lunch.active) and order == Order.CARRYING and (not lesson or (lesson.can_deliver() and (lesson.step==lesson.Step.DONE or lesson.round_index==0))),func(): _deliver())
	shop_marker = _add_marker(shop,"梯坎小面 · 店主",Color(.83,.65,.3))
	door_marker = _add_marker(destination,"山城里小院 · 1 号",Color(.4,.7,.7))
	select_free_address()
	bag = preload("res://scripts/takeaway_bag.gd").new()
	bag.name = "TakeawayFood"
	add_child(bag)
	bag.rotation.y=PI*.65
	bag.visible = false
	shopkeeper = preload("res://scripts/shopkeeper.gd").new()
	shopkeeper.name = "NoodleShopkeeper"
	add_child(shopkeeper)
	shopkeeper.global_position = _grounded(main._pickup + Vector3(-1.3,0,-.4))
	shopkeeper.rotation.y = PI*.65
	shopkeeper.autonomous=not main.capture_mode
	shopkeeper.configure_food(bag)
	add_child(condiments)
	condiments.setup(shopkeeper,bag)
	main.scene_identity["counter_r21"]={"stock_sha256":FileAccess.get_sha256("res://assets/counter_r21/chilli_station.glb"),"portion_sha256":FileAccess.get_sha256("res://assets/counter_r21/side_portion.glb"),"character_sha256":FileAccess.get_sha256(shopkeeper.MODEL_PATH)}
	var table: Node3D=load("res://assets/characters/serving_counter_r18.glb").instantiate()
	table.name="TakeawayTable"
	add_child(table)
	table.global_transform=shopkeeper.global_transform
	table.position+=shopkeeper.global_basis*Vector3(0,0,.46)
	var table_height: float=shopkeeper.food_end.y-shopkeeper.global_position.y
	table.scale.y=table_height/.795
	var counter_body: StaticBody3D=StaticBody3D.new()
	var counter_shape: CollisionShape3D=CollisionShape3D.new()
	var counter_box: BoxShape3D=BoxShape3D.new()
	counter_box.size=Vector3(.86,.79,.57)
	counter_shape.shape=counter_box
	counter_shape.position.y=.395
	counter_body.add_child(counter_shape)
	table.add_child(counter_body)
	var task_light: OmniLight3D=OmniLight3D.new()
	task_light.name="PackingTaskLight"
	task_light.light_color=Color(1,.91,.80)
	task_light.light_energy=float(main.applied_lighting.get("packing_task_light_energy",.12))
	task_light.omni_range=2.6
	task_light.omni_attenuation=1.2
	task_light.shadow_enabled=true
	task_light.shadow_bias=.02
	task_light.shadow_normal_bias=.08
	table.add_child(task_light)
	task_light.position=Vector3(-.11,1.87,.03)
	_make_scooter(main.get_node("City"))
	var district=main.get_node_or_null("City/OuterDistrict500")
	if district and district.has_meta("repair_court") and scooter:
		var site: Dictionary=district.get_meta("repair_court")
		var valve:=preload("res://scripts/district_500.gd").enu(site.valve)
		var service:=_target("workshop.tyre",valve,func():return "找师傅检查车胎",func():return not riding(),func():_service_tyre(valve))
		service.radius=2.15
	_make_doorbells()
	var board := main.get_node("City").find_child("R20_Post_notice", true, false) as MeshInstance3D
	if board != null:
		var face := board.to_global(board.mesh.get_aabb().get_center())
		var target := _target("residents.notice.upper", face + Vector3(.08,0,.045), func(): return "读居民告示", func(): return true, _read_resident_notice)
		target.radius = 1.65
		var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/lane_r20/rinse_fixture.json"))
		var outlet := Vector3(spec.outlet[0], spec.outlet[1], spec.outlet[2])
		rinse_tap = preload("res://scripts/rinse_tap.gd").new()
		add_child(rinse_tap)
		rinse_tap.setup(outlet, spec.ground_y)
		var tap_target := _target("residents.tap.upper", outlet, func(): return "关水" if rinse_tap.remaining>0. else "打开水龙头", func(): return true, rinse_tap.toggle)
		tap_target.radius = 1.35
		var seats: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/lane_r20/tree_seats.json"))
		for place: Dictionary in seats.places:
			var seat := Vector3(place.seat[0],place.seat[1],place.seat[2])
			var front := Vector3(place.front[0],place.front[1],place.front[2])
			var rest := _target("residents.bench."+str(place.arc),front+Vector3.UP*.76,func():return "坐一会儿",func():return not actor.seated,func():actor.sit_at(seat,front))
			rest.radius=1.18
		if main.art_profile.get("court_resident",false):
			court_resident=preload("res://scripts/court_resident.gd").new()
			court_resident.name="CourtResident"
			add_child(court_resident)
			court_resident.setup(self,main.capture_mode)
			main.scene_identity["court_resident"]={"model":FileAccess.get_sha256(court_resident.MODEL),"fit":FileAccess.get_sha256(court_resident.FIT),"controller":FileAccess.get_sha256("res://scripts/court_resident.gd")}

func _read_resident_notice() -> void:
	_say(RESIDENT_NOTICES[next_notice])
	toast_time = 6.5
	next_notice = (next_notice + 1) % RESIDENT_NOTICES.size()

func bind_walking_hand()->void:
	if actor.body_view:
		var sk:Skeleton3D=actor.body_view.find_children("*","Skeleton3D",true,false)[0]
		free_wrist=BoneAttachment3D.new()
		free_wrist.bone_name="Bip01 R Finger2"
		sk.add_child(free_wrist)

func _make_doorbells() -> void:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/geometry_repairs_r17.json"))
	if not data is Dictionary: return
	for entry: Dictionary in data.get("entrances",[]):
		var origin: Array = entry.origin
		var direction: Vector2 = Vector2(entry.outward[0],entry.outward[1])
		var tangent: Vector2 = Vector2(-direction.y,direction.x)
		var xy: Vector2 = Vector2(origin[0],origin[1])+direction*(-2.184)+tangent*(minf(1.15,float(entry.width_m)-.5)*.5+.19)
		var point: Vector3 = Vector3(xy.x,float(origin[2])+1.24,-xy.y)
		if str(entry.building)=="A04":point+=Unit.LANDING_SHIFT
		var id: String = "doorbell."+str(entry.building)+"."+str(entry.index)
		var bell: Node3D = _target(id,point,func(): return "按门铃",func(): return not (str(entry.building)=="A04" and order==Order.CARRYING),func(): _ring_bell(point))
		bell.radius=2.0

func _ring_bell(point: Vector3) -> void:
	if toast_time>.5: return
	_say("叮咚——屋内传来回应：哪位呀？")
	play_door_chime(point)

func play_door_chime(point: Vector3) -> void:
	var player: AudioStreamPlayer3D=AudioStreamPlayer3D.new()
	var tone: AudioStreamWAV=AudioStreamWAV.new()
	tone.format=AudioStreamWAV.FORMAT_16_BITS
	tone.mix_rate=22050
	var samples: PackedByteArray=PackedByteArray()
	samples.resize(22050)
	for i in range(11025):
		var time: float=float(i)/22050
		var freq: float=880.0 if time<.2 else 659.25
		var envelope: float=exp(-10.0*fmod(time,.2))*minf(time*80,1)
		samples.encode_s16(i*2,int(sin(TAU*freq*time)*envelope*2200))
	tone.data=samples
	player.stream=tone
	player.max_distance=8
	add_child(player)
	player.global_position=point
	player.finished.connect(player.queue_free)
	player.play()

func _grounded(point: Vector3) -> Vector3:
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(point+Vector3.UP*2,point-Vector3.UP*2,1)
	var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.position if not hit.is_empty() else point

func _target(id: String, point: Vector3, label: Callable, enabled: Callable, action: Callable, host: Node3D = null) -> Node3D:
	var target: Node3D = Target.new()
	target.interaction_id = id
	target.prompt = label
	target.enabled = enabled
	target.action = action
	(host if host != null else self).add_child(target)
	target.global_position = point
	manager.register(target)
	return target

func _service_tyre(counter: Vector3) -> void:
	if not scooter.parked or scooter.global_position.distance_to(counter)>8.5:
		_say("师傅：把车停在门前檐下，我给你看胎。")
		return
	var prior: float=scooter.tyre_pressure
	scooter.tyre_pressure=scooter.FULL_PRESSURE
	if lesson: lesson._save()
	_say("师傅：胎压正常，可以走了。" if prior>=scooter.FULL_PRESSURE-.02 else "师傅：车胎已充好，%.1f → %.1f bar。" % [prior,scooter.tyre_pressure])

func _make_scooter(city: Node3D) -> void:
	var meshes: Array[Node] = city.find_children("CQF_Scooter_99_*","MeshInstance3D",true,false)
	if meshes.is_empty():
		push_error("R16 scooter source meshes missing")
		return
	scooter = Scooter.new()
	scooter.name = "PlayerElectricScooter"
	add_child(scooter)
	# Move the playable vehicle out of the narrow R15 service recess into the
	# open noodle-shop forecourt. Other six parked meshes retain authored sites.
	scooter.global_position = _grounded(Vector3(-20.5,12,59)) + Vector3.UP*.03
	scooter.rotation.y = -PI/2
	scooter.safe_park_position = scooter.global_position
	for mesh in meshes:
		# The separate authored asset retains the original geometry with wheel,
		# steering and stand pivots. Other six parked city scooters are unchanged.
		mesh.queue_free()
	scooter.message.connect(_say)
	var target: Node3D = _target("vehicle.scooter.99",scooter.global_position+Vector3.UP,func(): return lesson.vehicle_prompt() if lesson else "骑电瓶车",func(): return not riding() and (not lesson or lesson.can_mount()),_enter_or_load_scooter,scooter)
	vehicle_marker=_add_marker(target,"电瓶车",Color(.4,.8,.72))

func _enter_or_load_scooter() -> void:
	if lesson: lesson.use_bike()
	else: scooter.enter(actor)

func _add_marker(parent: Node3D, text: String, color: Color) -> Label3D:
	var label: Label3D = Label3D.new()
	label.text = text
	label.font = owner_scene.UI_FONT
	label.font_size = 40
	label.pixel_size = .006
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.modulate = color
	label.position.y = 1.0
	label.visible = not owner_scene.capture_mode
	parent.add_child(label)
	return label

func _box(parent: Node3D, position: Vector3, size: Vector3, color: Color) -> void:
	var mesh: MeshInstance3D = MeshInstance3D.new()
	var box: BoxMesh = BoxMesh.new()
	box.size = size
	mesh.mesh = box
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = .85
	mesh.material_override = mat
	mesh.position = position
	parent.add_child(mesh)

func _shop_prompt() -> String:
	if passage and passage.offered:return "接邻里托送　B 返回"
	if lunch and (lunch.preview or lunch.active):return lunch.shop_prompt()
	if lunch and order==Order.DELIVERED:return "接一单　G 午市拼送　B 穿楼托送"
	if order==Order.READY and condiments.state==condiments.State.ON_COUNTER:return "把另装的辣子放进袋里"
	if order==Order.READY and condiments.state==condiments.State.ADDING:return "正在放调料盒"
	return "接下一单" if order==Order.DELIVERED else ["与店主接单","店主正在打包","领取打包好的餐食"][order]

func _shop_action() -> void:
	if passage and passage.offered:
		passage.begin()
		return
	if passage:passage.last_receipt=""
	if lunch and lunch.preview:
		lunch.accept()
		return
	if lunch and lunch.active:
		lunch.pickup()
		return
	if lunch and not lunch.recap.is_empty():
		lunch.recap=""
		for parcel in lunch.parcels:parcel.hide()
		lesson._save()
	if order == Order.AVAILABLE or order == Order.DELIVERED:
		var teaching:bool=lesson and lesson.step==lesson.Step.SHOP
		if not teaching:select_free_address()
		var separate_chilli: bool=lesson.round_index==1 if teaching else delivered_count%2==1
		var ticket_number:=delivered_count+1
		if lesson:ticket_number=lesson.receipt() if teaching else 2*(delivered_count+1)
		bag.write_ticket(ticket_number,separate_chilli)
		condiments.begin(separate_chilli)
		shopkeeper.play_state("serve")
		order = Order.PREPARING
		preparation = shopkeeper.SERVE_SECONDS+.15
		owner_scene._delivery_stage = 0
		_say("店主：这碗辣子另装。台上那盒，取餐时帮我放进袋里。" if separate_chilli else "店主：山城里小院一单元，一碗小面，马上打包好。")
		if not teaching:
			bag.ticket.text+=" · "+Unit.ADDRESSES[free_flat]
			_say("店主：这袋送到山城里小院%s，到了敲门。"%Unit.ADDRESSES[free_flat])
		if teaching and lesson.round_index==0:bag.ticket.text+=" · 201"
		if teaching and lesson.round_index>0:
			_say("店主：%03d 号，%s，%s。" % [lesson.receipt(),lesson.ORDER_NAMES[lesson.round_index],"辣子另装" if separate_chilli else "看小票放乙位"])
			bag.ticket.text+=" · 乙"
	elif order == Order.READY:
		if condiments.state==condiments.State.ON_COUNTER:
			condiments.pack()
			_say("辣子另装，放稳再提。")
			return
		if condiments.state==condiments.State.ADDING:return
		shopkeeper.play_state("greet")
		order = Order.CARRYING
		bag.visible = false
		owner_scene._delivery_stage = 1
		_say("已取餐 · 送往%s" % lesson.ORDER_NAMES[lesson.round_index] if lesson and lesson.step==lesson.Step.SHOP else "已取餐 · 山城里小院"+Unit.ADDRESSES[free_flat])

func select_free_address() -> void:
	free_flat=posmod(delivered_count-3,2) if delivered_count>=3 else posmod(delivered_count,2)
	free_answered=false
	shelf_time=-1.
	destination.global_position=Unit.DOOR_POINTS[free_flat]
	destination.radius=.90
	door_marker.text=Unit.ADDRESSES[free_flat]
	door_marker.hide()

func free_delivery_prompt()->String:
	if passage and passage.stage==passage.Stage.CARRY:return "把豆花饭放稳" if free_answered else "在 301 门前报号"
	return "把餐放在门边搁板上" if free_answered else "在 %d 敲门报号" % (201+free_flat)

func free_handover()->bool:
	if riding() or not manager.reachable(destination) or shelf_time>=0.:return false
	var sight:Vector3=actor.camera.global_position.direction_to(destination.global_position)
	if (-actor.camera.global_basis.z).dot(sight)<.72:
		_say("看一下户门上的门牌。")
		return false
	var crossing:bool=passage!=null and passage.stage==passage.Stage.CARRY
	var support:Vector3=passage.SHELF if crossing else Unit.SHELVES[free_flat]
	if not free_answered:
		free_answered=true
		play_door_chime(destination.global_position)
		destination.global_position=support+Vector3.UP*.12
		_say("%d 住户：是我的，麻烦放在门边搁板上，谢谢。"%(301 if crossing else 201+free_flat))
		if crossing:lesson._save()
		return false
	if (actor.body.global_position-support).slide(Vector3.UP).length()>.66:
		_say("走近门边的搁板再放餐。")
		return false
	shelf_start=bag.global_position
	shelf_yaw=bag.rotation.y
	shelf_time=0.
	return false

func _free_parcel(dt:float)->void:
	if order!=Order.CARRYING or (lesson and lesson.step!=lesson.Step.DONE):return
	var batch:bool=lunch!=null and lunch.active
	var guide:Node3D=lesson.demo if lesson else null
	var left:bool=batch and lunch.selected==lunch.left_ticket and shelf_time>=0.
	var ik:SkeletonIK3D
	var goal:Node3D
	if guide and guide.pupil_hand:
		ik=guide.pupil_ik if left else guide.pupil_hang_ik
		goal=guide.pupil_goal if left else guide.pupil_hang_goal
	if riding():
		if shelf_time>=0. and ik:ik.stop()
		shelf_time=-1.
		bag.hide()
		return
	var right_occupied:bool=not batch or lunch.right_hand()>=0
	bag.visible=right_occupied
	if right_occupied and (shelf_time<0. or left):
		var grip:Vector3=guide.pupil_grip() if guide else (free_wrist.global_position if free_wrist else actor.body.to_global(Vector3(.28,.86,-.1)))
		bag.rotation.y=guide.pupil_yaw if guide else actor.body.rotation.y
		bag.global_position=grip-Vector3.UP*.331
	if shelf_time<0.:return
	var landing:Vector3=lunch.support(lunch.selected) if batch else Unit.SHELVES[free_flat]
	if passage and passage.stage==passage.Stage.CARRY:landing=passage.SHELF
	if not manager.reachable(lunch.release_target if batch else destination):
		shelf_time=-1.
		if ik:ik.stop()
		return
	shelf_time+=dt
	var progress:=smoothstep(0.,1.,minf(1.,shelf_time/.85))
	var position_:Vector3=shelf_start.lerp(landing,progress)+Vector3.UP*.06*sin(progress*PI)
	var placing:Node3D=lunch.parcels[lunch.selected] if left else bag
	placing.global_position=position_
	placing.rotation.y=lerp_angle(shelf_yaw,0. if batch and lunch.selected==0 else PI/2,progress)
	if ik:
		var wrist_to_grip:Vector3=guide.pupil_knuckle-guide.pupil_wrist if left else guide.pupil_grasp-guide.pupil_right_wrist
		goal.global_position=position_+Vector3.UP*.331-wrist_to_grip
		if not ik.is_running():ik.start()
		ik.influence=smoothstep(0.,.22,shelf_time)*(1.-smoothstep(.85,1.17,shelf_time))
	if shelf_time>=1.17:
		if ik:ik.stop()
		shelf_time=-1.
		if batch:lunch.settle()
		else:_credit_delivery()

func _deliver() -> void:
	if order != Order.CARRYING:
		return
	if lesson and not lesson.student_handover(): return
	if not lesson and not free_handover():return
	_credit_delivery()

func _credit_delivery()->void:
	if passage and passage.stage==passage.Stage.CARRY:
		passage.settle()
		return
	order = Order.DELIVERED
	delivered_count += 1
	earnings += 8
	owner_scene._delivery_stage = 2
	_say("已送达 · 配送收入 +8 元")
	if lesson: lesson.delivery_finished()

func _process(delta: float) -> void:
	if passage and passage.offered and not passage.available():passage.offered=false
	if lunch:lunch.tick(delta)
	_free_parcel(delta)
	toast_time = maxf(0,toast_time-delta)
	if is_instance_valid(vehicle_marker):vehicle_marker.visible=not riding() and not owner_scene.capture_mode
	if lesson and not owner_scene.capture_mode:
		shop_marker.visible = shop.available()
		door_marker.visible = lesson.step!=lesson.Step.DONE and lesson.round_index>0 and order == Order.CARRYING and lesson.can_deliver()
		if not lesson.can_mount(): vehicle_marker.visible = false
	if not owner_scene.capture_mode:
		shopkeeper.greet_nearby(actor.camera.global_position)
	if order == Order.PREPARING:
		preparation -= delta
		if preparation <= 0:
			order = Order.READY
			bag.visible = true

func _say(text: String) -> void:
	toast = text
	toast_time = 3.0

func riding() -> bool:
	return is_instance_valid(scooter) and is_instance_valid(scooter.rider)

func interact() -> bool:
	if actor.seated:
		actor.stand_up()
		return true
	if riding():
		return scooter.exit_vehicle()
	return manager.interact()

func ui() -> Dictionary:
	var target: Node3D = manager.select() if not riding() else null
	var prompt: String = "E  " + target.label() if target != null else ""
	if riding():
		prompt = "%.0f km/h · W S 前进/倒车 · A D 转向 · 空格刹车 · P 停车 · E 下车" % (absf(scooter.speed)*3.6)
	if toast_time>0:
		prompt = toast
	if actor.seated:
		prompt = "E  起身"
	var destination_point: Vector3 = destination.global_position if order==Order.CARRYING else shop.global_position
	var distance: float = Vector2(actor.body.global_position.x,actor.body.global_position.z).distance_to(Vector2(destination_point.x,destination_point.z))
	var objective: String = ["到小面馆找店主","等待店主打包","领取餐食","山城里小院 · "+Unit.ADDRESSES[free_flat],"已送达 · 回面馆接下一单"][order]
	for handoff: Node3D in [shancheng,riverside_tea,outer_market_handoff]:
		if handoff:
			var local_panel: String=handoff.panel()
			if not local_panel.is_empty():
				return {"objective":local_panel,"prompt":prompt}
	if passage and (passage.offered or passage.stage!=passage.Stage.IDLE or (not passage.last_receipt.is_empty() and not lunch.preview and not lunch.active)):
		return {"objective":passage.panel(),"prompt":prompt}
	if lunch:
		if lunch.preview or lunch.active:return {"objective":lunch.panel(),"prompt":prompt}
		if not lunch.recap.is_empty():return {"objective":lunch.recap,"prompt":prompt}
	if lesson and lesson.uses_hud():
		if riding() and toast_time <= 0.0:
			prompt = "%.0f km/h" % (absf(scooter.speed)*3.6)
		return {"objective":lesson.objective(),"prompt":prompt}
	return {"objective":objective+" · %d m" % roundi(distance)+("\n今日 %d 单 · %d 元" % [delivered_count,earnings] if delivered_count>0 else ""),"prompt":prompt}

func _unhandled_input(event: InputEvent) -> void:
	if lunch and not public_handoff_in_progress() and event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode==KEY_B and passage and passage.view_offer():
			get_viewport().set_input_as_handled()
			return
		if event.physical_keycode==KEY_G and passage:passage.offered=false
		if (event.physical_keycode==KEY_G and lunch.toggle_preview()) or (event.physical_keycode==KEY_V and lunch.change_ticket()):
			get_viewport().set_input_as_handled()
			return
	if riding() and event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_P:
		scooter.park()
		get_viewport().set_input_as_handled()
