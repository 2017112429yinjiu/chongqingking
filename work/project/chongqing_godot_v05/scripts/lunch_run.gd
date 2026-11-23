extends Node3D
## Three independent tickets at the existing noodle counter, court rack and occupied flats.
const Unit = preload("res://scripts/unit_interior.gd")
const Bag = preload("res://scripts/takeaway_bag.gd")
const ADDRESSES := ["球场下巷 · 取餐架", "一单元 201", "一单元 202"]
const MEALS := ["杂酱面", "清汤抄手", "豌杂面"]
const FEES := [9, 12, 11]
const DUE := [65, 115, 150]
const READY_AT := [0, 5, 22]
enum State { COUNTER, HELD, PAID }
var game: Node3D
var rack: Node3D
var parcels: Array[Node3D] = []
var counters: Array[Vector3] = []
var active := false
var preview := false
var selected := 0
var left_ticket := -1
var first_number := 0
var elapsed := 0.0
var saved_at := 0.0
var states := [State.COUNTER, State.COUNTER, State.COUNTER]
var awards := [0, 0, 0]
var answered := [false, false, false]
var release_target: Node3D
var recap := ""

func setup(world: Node3D, court: Node3D) -> void:
	game = world
	rack = court
	var table: Node3D = game.get_node("TakeawayTable")
	# Two hot orders share the worktop; the later bag uses the timber pick-up shelf.
	var spots := [Vector3(-.295,.795,.135),Vector3(-.037,.795,.135),Vector3(.12,.2215,.065)]
	for i in 3:
		var parcel: Node3D = Bag.new()
		add_child(parcel)
		parcel.hide()
		parcels.append(parcel)
		counters.append(table.to_global(spots[i]))
		var point: Vector3 = rack.call_point+Vector3.BACK*.04 if i==0 else Unit.DOOR_POINTS[i-1]
		var target: Node3D = game._target("lunch.notify.%d"%i, point, func(): return "按呼叫键报号" if i==0 else "敲门报单号", func(): return active and hand_count()>0 and not answered[i], notify_customer.bind(i))
		target.radius = .95 if i==0 else .90
		var spot: Node3D = game._target("lunch.place.%d"%i, support(i)+Vector3.UP*.12, func(): return "把餐放在甲位" if i==0 else "把餐放到门边搁板", func(): return active and answered[i] and states[i]==State.HELD, place.bind(i))
		spot.radius = .93
	var other: Node3D = game._target("lunch.court.wrong_bay",rack.slots[1]+Vector3.UP*.12,func():return "核对乙位",func():return active and answered[0] and states[0]==State.HELD,func():game._say("收餐人留的是甲位，看一下架上的字。"))
	other.radius=.93

func ticket_number(i:int)->int:
	return first_number+2*i

func set_route_controls(enabled:bool)->void:
	game.actor.review_shortcuts=not enabled
	game.owner_scene.view_picker.get_parent().visible=not enabled
	game.owner_scene._mode_changed(game.actor.walking)

func support(i: int) -> Vector3:
	return rack.slots[0] if i==0 else Unit.SHELVES[i-1]

func hand_count() -> int:
	return states.count(State.HELD)

func right_hand() -> int:
	for i in 3:
		if states[i]==State.HELD and i!=left_ticket:return i
	return -1

func at_counter() -> bool:
	return not game.riding() and game.manager.reachable(game.shop)

func can_offer() -> bool:
	return not active and game.order in [game.Order.AVAILABLE,game.Order.DELIVERED] and at_counter()

func toggle_preview() -> bool:
	if not can_offer():return false
	preview=not preview
	game.toast_time=0.
	return true

func change_ticket() -> bool:
	if not active or game.shelf_time>=0.:return false
	for offset in range(1,4):
		var i: int=(selected+offset)%3
		if states[i]!=State.PAID:
			selected=i
			break
	game.toast_time=0.
	sync_hand()
	game.lesson._save()
	return true

func accept() -> void:
	if not preview or not can_offer():return
	preview=false
	active=true
	set_route_controls(true)
	recap=""
	first_number=2*(game.delivered_count+1)
	elapsed=0.
	saved_at=0.
	selected=0
	left_ticket=-1
	states.fill(State.COUNTER)
	awards.fill(0)
	answered.fill(false)
	game.bag.hide()
	for i in 3:write_ticket(parcels[i],i)
	sync_hand()
	game._say("店主：球场的杂酱好了。抄手先起锅，豌杂还要等一哈。")
	game.lesson._save()

func write_ticket(parcel: Node3D, i:int) -> void:
	parcel.ticket.font_size=56
	parcel.ticket.pixel_size=.00044
	parcel.ticket.font=preload("res://assets/fonts/first_shift.otf")
	parcel.ticket.text="%03d  %s\n%s"%[ticket_number(i),MEALS[i],["球场 · 甲","201","202"][i]]

func pickup() -> void:
	if not active or not at_counter():return
	if states[selected]!=State.COUNTER:
		game._say("这张已取。按 V 翻到还在面馆的小票。")
	elif elapsed<READY_AT[selected]:
		game._say("店主：%s还在锅里，约 %d 秒。"%[MEALS[selected],ceili(READY_AT[selected]-elapsed)])
	elif hand_count()>=2:
		game._say("两袋已经提满。这份先留在柜上，送完再来取。")
	else:
		if right_hand()>=0:left_ticket=selected
		states[selected]=State.HELD
		sync_hand()
		game._say("已取 %03d 号%s · %s"%[ticket_number(selected),MEALS[selected],ADDRESSES[selected]])
		game.lesson._save()

func sync_hand() -> void:
	var right:=right_hand()
	game.order=game.Order.CARRYING if hand_count()>0 else game.Order.DELIVERED
	game.owner_scene._delivery_stage=int(hand_count()>0)
	if right>=0:write_ticket(game.bag,right)
	else:game.bag.hide()
	show_parcels()

func show_parcels() -> void:
	var right:=right_hand()
	for i in 3:
		var parcel:=parcels[i]
		match states[i]:
			State.COUNTER:
				parcel.visible=elapsed>=READY_AT[i]
				parcel.global_position=counters[i]
				parcel.rotation.y=game.shopkeeper.rotation.y
			State.HELD:
				parcel.visible=game.riding() or i!=right
				if game.riding():
					var box:Node3D=game.lesson.demo.pupil_box.box
					var slot_z:=.48 if i==states.find(State.HELD) else .68
					parcel.global_transform=box.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.866,slot_z))
				elif parcel.visible and (game.shelf_time<0. or selected!=i):
					var demo:Node3D=game.lesson.demo
					parcel.global_position=(demo.pupil_knuckle if demo.pupil_hand else game.actor.body.to_global(Vector3(-.28,.86,-.10)))-Vector3.UP*.331
					parcel.rotation.y=demo.pupil_yaw
			State.PAID:
				parcel.show()
				parcel.global_position=support(i)
				parcel.rotation.y=0. if i==0 else PI/2

func notify_customer(i:int) -> void:
	if selected!=i or states[i]!=State.HELD:
		game._say("这里收%s。看看袋上的小票，按 V 换单。"%MEALS[i])
		return
	var point:Vector3=rack.call_point if i==0 else Unit.DOOR_POINTS[i-1]
	if not looking(point):game._say("面向呼叫键或门牌再报号。");return
	game.play_door_chime(point)
	answered[i]=true
	game._say(["球友：杂酱是我的，放甲位，我打完这球就来。","201：清汤抄手是我的，谢谢，放门边搁板。","202：豌杂到了？搁门边，我马上拿。"][i])
	game.lesson._save()

func looking(point:Vector3)->bool:
	var camera:Camera3D=game.actor.camera
	return (-camera.global_basis.z).dot(camera.global_position.direction_to(point))>=.72

func place(i:int)->void:
	if game.shelf_time>=0.:return
	if selected!=i or states[i]!=State.HELD:
		game._say("袋上的收餐地址对不上，按 V 核对。")
		return
	release_target=game.manager.current
	if not looking(release_target.global_position) or game.actor.body.global_position.slide(Vector3.UP).distance_to(support(i).slide(Vector3.UP))>.68:
		game._say("靠近搁板，看着放餐的位置。")
		return
	var parcel:Node3D=parcels[i] if i==left_ticket else game.bag
	game.shelf_start=parcel.global_position
	game.shelf_yaw=parcel.rotation.y
	game.shelf_time=0.

func settle() -> void:
	if not active or states[selected]!=State.HELD or not answered[selected]:return
	var i:=selected
	states[i]=State.PAID
	if left_ticket==i:left_ticket=-1
	awards[i]=FEES[i] if elapsed<=DUE[i] else FEES[i]-3
	game.delivered_count+=1
	game.earnings+=awards[i]
	var receipt:="%03d 已送达 · %s +%d 元"%[ticket_number(i),"准时" if awards[i]==FEES[i] else "超时",awards[i]]
	var pending:=states.find(State.HELD)
	if pending<0:pending=states.find(State.COUNTER)
	if pending>=0:selected=pending
	sync_hand()
	if pending<0:
		active=false
		set_route_controls(false)
		game.owner_scene._delivery_stage=2
		var on_time:=0
		for j in 3:on_time+=int(awards[j]==FEES[j])
		recap="午市收工 · %d / 3 单准时\n球场 %d 元　201 %d 元　202 %d 元\n本趟 %d 元 · 今日 %d 元"%[on_time,awards[0],awards[1],awards[2],awards[0]+awards[1]+awards[2],game.earnings]
		game.select_free_address()
	game._say(receipt)
	game.lesson._save()

func tick(dt:float)->void:
	if preview and not at_counter():preview=false
	if not active:return
	elapsed+=dt
	show_parcels()
	if elapsed-saved_at>=5.:
		saved_at=elapsed
		game.lesson._save()

func shop_prompt()->String:
	if preview:return "接下这三单　G 收起"
	if states[selected]==State.COUNTER:return "取 %03d 号%s　V 翻小票"%[ticket_number(selected),MEALS[selected]]
	return "核对出餐单　V 翻小票"

func panel()->String:
	var lines:=PackedStringArray()
	if preview:
		lines.append("梯坎小面 · 午市三单")
		for i in 3:
			var dist:=Vector2(game.shop.global_position.x,game.shop.global_position.z).distance_to(Vector2(support(i).x,support(i).z))
			lines.append("%s　%d 米　%d 元"%[ADDRESSES[i],roundi(dist),FEES[i]])
		lines.append("E 接这趟　G 返回")
	elif active:
		lines.append("午市拼送　手中 %d / 2　V 翻小票"%hand_count())
		for i in 3:
			var remaining:float=DUE[i]-elapsed
			var secs:=ceili(absf(remaining))
			var state:String=["待取" if elapsed>=READY_AT[i] else "备餐","已取","已送"][states[i]]
			var clock_text:="%d:%02d"%[absi(secs)/60,absi(secs)%60]
			var timing:="超 "+clock_text if remaining<0. else clock_text
			lines.append("%s %s　%s　%s"%["›" if selected==i else " ",["球场甲","201室","202室"][i],state,("+%d元"%awards[i] if states[i]==State.PAID else timing)])
		lines.append("%03d · %s · %s"%[ticket_number(selected),MEALS[selected],ADDRESSES[selected]])
	return "\n".join(lines)

func store_progress(record:ConfigFile)->void:
	if not active and recap.is_empty():return
	for key:String in ["active","recap","first_number","elapsed","selected","left_ticket","states","awards","answered"]:
		record.set_value("lunch",key,get(key))
	if active and game.actor.walking and not game.riding():record.set_value("lunch","foot",game.actor.body.global_position)

func _notification(what:int)->void:
	if what==NOTIFICATION_WM_CLOSE_REQUEST and active and is_instance_valid(game):
		game.lesson._save()

func restore(record:ConfigFile)->void:
	if not record.has_section("lunch"):return
	recap=record.get_value("lunch","recap","")
	var continuing:bool=record.get_value("lunch","active",false)
	if not continuing and recap.is_empty():return
	for key:String in ["states","awards","answered"]:
		var list:Variant=record.get_value("lunch",key,[])
		if not list is Array or list.size()!=3:return
	var saved_states:Array=record.get_value("lunch","states")
	if saved_states.count(State.HELD)>2 or not saved_states.all(func(s):return s in [State.HELD,State.PAID,State.COUNTER]):return
	states=saved_states
	left_ticket=record.get_value("lunch","left_ticket",states.rfind(State.HELD) if hand_count()==2 else -1)
	if left_ticket<0 or left_ticket>=3 or states[left_ticket]!=State.HELD:left_ticket=-1
	awards=record.get_value("lunch","awards")
	answered=record.get_value("lunch","answered")
	first_number=record.get_value("lunch","first_number",8)
	elapsed=maxf(0.,record.get_value("lunch","elapsed",0.))
	saved_at=elapsed
	selected=clampi(record.get_value("lunch","selected",0),0,2)
	for i in 3:write_ticket(parcels[i],i)
	if not continuing:
		show_parcels()
		return
	active=true
	set_route_controls(true)
	sync_hand()
	if record.has_section_key("lunch","foot"):
		var foot:Vector3=record.get_value("lunch","foot")
		game.lesson._walk_from(foot,foot+Vector3.UP*1.3+Vector3.FORWARD)
