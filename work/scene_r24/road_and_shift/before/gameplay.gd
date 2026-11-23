extends Node3D
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

func setup(main: Node3D) -> void:
	owner_scene = main
	actor = main.explorer
	manager = Manager.new()
	manager.actor = actor
	add_child(manager)
	shop = _target("shop.noodle",main._pickup+Vector3.UP,func(): return _shop_prompt(),func(): return order != Order.CARRYING and (not lesson or lesson.can_order()),func(): _shop_action())
	destination = _target("delivery.home",main._dropoff+Vector3.UP,func(): return lesson.delivery_prompt() if lesson else "交付餐食",func(): return order == Order.CARRYING and (not lesson or lesson.can_deliver()),func(): _deliver())
	shop_marker = _add_marker(shop,"梯坎小面 · 店主",Color(.83,.65,.3))
	door_marker = _add_marker(destination,"山城里小院 · 1 号",Color(.4,.7,.7))
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

func _make_doorbells() -> void:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://assets/geometry_repairs_r17.json"))
	if not data is Dictionary: return
	for entry: Dictionary in data.get("entrances",[]):
		var origin: Array = entry.origin
		var direction: Vector2 = Vector2(entry.outward[0],entry.outward[1])
		var tangent: Vector2 = Vector2(-direction.y,direction.x)
		var xy: Vector2 = Vector2(origin[0],origin[1])+direction*(-2.184)+tangent*(minf(1.15,float(entry.width_m)-.5)*.5+.19)
		var point: Vector3 = Vector3(xy.x,float(origin[2])+1.24,-xy.y)
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
	if order==Order.READY and condiments.state==condiments.State.ON_COUNTER:return "把另装的辣子放进袋里"
	if order==Order.READY and condiments.state==condiments.State.ADDING:return "正在放调料盒"
	return "接下一单" if order==Order.DELIVERED else ["与店主接单","店主正在打包","领取打包好的餐食"][order]

func _shop_action() -> void:
	if order == Order.AVAILABLE or order == Order.DELIVERED:
		var separate_chilli: bool=delivered_count%2==1
		bag.write_ticket(2 if lesson and lesson.step == lesson.Step.SHOP else delivered_count+1,separate_chilli)
		condiments.begin(separate_chilli)
		shopkeeper.play_state("serve")
		order = Order.PREPARING
		preparation = shopkeeper.SERVE_SECONDS+.15
		owner_scene._delivery_stage = 0
		_say("店主：这碗辣子另装。台上那盒，取餐时帮我放进袋里。" if separate_chilli else "店主：山城里小院 1 号，一碗小面，马上打包好。")
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
		_say("已取餐 · 送往上层住宅")

func _deliver() -> void:
	if order != Order.CARRYING:
		return
	if lesson and not lesson.student_handover(): return
	order = Order.DELIVERED
	delivered_count += 1
	earnings += 8
	if lesson: lesson.delivery_finished()
	owner_scene._delivery_stage = 2
	_say("住户：谢谢，辛苦了！ · 配送收入 +8 元")

func _process(delta: float) -> void:
	toast_time = maxf(0,toast_time-delta)
	if is_instance_valid(vehicle_marker):vehicle_marker.visible=not riding() and not owner_scene.capture_mode
	if lesson and not owner_scene.capture_mode:
		shop_marker.visible = lesson.can_order()
		door_marker.visible = order == Order.CARRYING and lesson.can_deliver()
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
	var distance: float = actor.body.global_position.distance_to(destination_point)
	var objective: String = ["到小面馆找店主","等待店主打包","领取餐食","送往山城里小院 1 号","已送达 · 回面馆接下一单"][order]
	if lesson and lesson.uses_hud():
		if riding() and toast_time <= 0.0:
			prompt = "%.0f km/h" % (absf(scooter.speed)*3.6)
		return {"objective":lesson.objective(),"prompt":prompt}
	return {"objective":objective+" · %d m" % roundi(distance)+("\n今日 %d 单 · %d 元" % [delivered_count,earnings] if delivered_count>0 else ""),"prompt":prompt}

func _unhandled_input(event: InputEvent) -> void:
	if riding() and event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_P:
		scooter.park()
		get_viewport().set_input_as_handled()
