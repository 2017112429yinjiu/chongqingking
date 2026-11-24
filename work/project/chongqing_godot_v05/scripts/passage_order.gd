extends Node3D
const Unit=preload("res://scripts/unit_interior.gd")
const DOOR:=Vector3(-58.86,24.17,14.10)
const SHELF:=Vector3(-58.84,23.80,14.97)
const PAY:=16
enum Stage { IDLE, COLLECT, CARRY }
var game:Node3D
var stage:=Stage.IDLE
var offered:=false
var last_receipt:=""
var receipt:=0
var pickup:Node3D

func setup(world:Node3D)->void:
	game=world
	pickup=game._target("passage.collect.202",Unit.SHELVES[1]+Vector3.UP*.13,
		func():return "取 202 门边的豆花饭",func():return stage==Stage.COLLECT,collect)
	pickup.radius=.92

func available()->bool:
	return stage==Stage.IDLE and game.lunch.can_offer()

func view_offer()->bool:
	if not available():return false
	offered=not offered
	game.lunch.preview=false
	game.toast_time=0
	return true

func begin()->void:
	offered=false
	last_receipt=""
	game.lunch.recap=""
	for parcel in game.lunch.parcels:parcel.hide()
	game.lunch.set_route_controls(true)
	stage=Stage.COLLECT
	receipt=2*(game.delivered_count+1)
	game.order=game.Order.AVAILABLE
	put_pickup_on_shelf()
	game._say("202 蒋嬢嬢：豆花饭我放门边了。从下院进来，二楼见。")
	game.lesson._save()

func put_pickup_on_shelf()->void:
	game.bag.write_ticket(receipt,false)
	game.bag.ticket.font=preload("res://assets/fonts/first_shift.otf")
	game.bag.ticket.text="%03d 豆花饭\n一单元 301"%receipt
	game.bag.global_position=Unit.SHELVES[1]
	game.bag.rotation.y=PI/2
	game.bag.show()

func collect()->void:
	if stage!=Stage.COLLECT or not game.manager.reachable(pickup):return
	if not game.lunch.looking(pickup.global_position):
		game._say("看看 202 门边搁板上的小票。")
		return
	stage=Stage.CARRY
	game.order=game.Order.CARRYING
	game.owner_scene._delivery_stage=1
	game.free_answered=false
	game.shelf_time=-1.
	game.destination.global_position=DOOR
	game.destination.radius=.90
	game._say("蒋嬢嬢：走廊往院门方向，有楼梯上三楼。你要是从背巷过来，蓝砖楼的天桥也通罗师傅家。")
	game.toast_time=7.
	game.lesson._save()

func settle()->void:
	stage=Stage.IDLE
	game.order=game.Order.DELIVERED
	game.delivered_count+=1
	game.earnings+=PAY
	game.owner_scene._delivery_stage=2
	game.lunch.set_route_controls(false)
	game.select_free_address()
	last_receipt="罗师傅已收餐 · +%d 元\n今日 %d 单 · %d 元"%[PAY,game.delivered_count,game.earnings]
	game._say("罗师傅：收到。辛苦你跑上跑下，坐会儿再走嘛。")
	game.lesson._save()

func panel()->String:
	if offered:return "邻里托送 · 豆花饭\n取　小院一单元 202\n送　小院一单元 301　16 元\nE 接这单　B 返回"
	if stage==Stage.COLLECT:return "邻里托送 · 到一单元 202 取餐\n从下院进单元，餐在二楼门边。"
	if stage==Stage.CARRY:
		return "邻里托送 · 一单元 301\n本楼走住户楼梯上三楼。\n从背巷来也可借蓝砖楼天桥。" if not game.free_answered else "罗师傅已应门\n把豆花饭放在 301 门边搁板。"
	return last_receipt

func save_to(record:ConfigFile)->void:
	if stage==Stage.IDLE and last_receipt.is_empty():return
	record.set_value("passage","stage",stage)
	record.set_value("passage","receipt",receipt)
	record.set_value("passage","answered",game.free_answered)
	record.set_value("passage","summary",last_receipt)
	if stage!=Stage.IDLE and game.actor.walking and not game.riding():
		record.set_value("passage","foot",game.actor.body.global_position)

func restore(record:ConfigFile)->void:
	if not record.has_section("passage") or game.lunch.active:return
	last_receipt=record.get_value("passage","summary","")
	stage=clampi(record.get_value("passage","stage",0),Stage.IDLE,Stage.CARRY)
	if stage==Stage.IDLE:return
	receipt=record.get_value("passage","receipt",2*(game.delivered_count+1))
	game.lunch.set_route_controls(true)
	put_pickup_on_shelf()
	game.order=game.Order.AVAILABLE
	if stage==Stage.CARRY:
		game.order=game.Order.CARRYING
		game.owner_scene._delivery_stage=1
		game.free_answered=record.get_value("passage","answered",false)
		game.destination.global_position=SHELF+Vector3.UP*.12 if game.free_answered else DOOR
	if record.has_section_key("passage","foot"):
		var foot:Vector3=record.get_value("passage","foot")
		game.lesson._walk_from(foot,foot+Vector3.UP*1.3+Vector3.FORWARD)

func _notification(what:int)->void:
	if what==NOTIFICATION_WM_CLOSE_REQUEST and stage!=Stage.IDLE and is_instance_valid(game):
		game.lesson._save()
