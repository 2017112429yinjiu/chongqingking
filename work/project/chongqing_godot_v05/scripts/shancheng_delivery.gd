extends Node3D
## A public-walkway handoff. The two alternatives rejoin at the same physical shelf.
enum Stage { AVAILABLE, CARRYING, DELIVERED }
var stage:=Stage.AVAILABLE
var game: Node3D
var stops: Array
var parcel: Node3D
var delivered_parcel: Node3D
var receiver: Node3D
var sender: Node3D
var job: Dictionary
const SHANCHENG := {
	"id":"shancheng", "sender":"山城巷取件台", "receiver":"仁爱堂外 · 公共步道交接架",
	"pickup":"取件 · 步行送往仁爱堂外（6元）", "dropoff":"放上交接架 · 完成托送",
	"ticket":"步道托送 · 公共交接架", "receipt":"已签收 · 山城巷", "reward":6,
	"carrying":"山城巷托送 · 仁爱堂外公共交接架\n沿山城巷或第三步道汇合后上行",
	"ready":"山城巷 · 步道托送\n取件台 → 仁爱堂外交接架", "done":"山城巷托送已完成 · 6 元",
	"collected":"已取件 · 可沿山城巷直行，也可走山城第三步道", "paid":"步道交接完成 · 配送收入 +6 元",
}
const RIVERSIDE_TEA := {
	"id":"riverside_tea", "sender":"江岸茶摊 · 取件", "receiver":"江岸铺带 · 交接架",
	"pickup":"领取包好的茶饮（6元）", "dropoff":"将茶饮放上交接架",
	"ticket":"江岸茶摊 · 茶饮托送", "receipt":"已签收 · 江岸茶摊", "reward":6,
	"carrying":"江岸茶摊托送\n沿陆侧铺带前往交接架", "ready":"江岸茶摊 · 茶饮托送\n摊主 → 陆侧铺带交接架",
	"done":"茶饮已送达 · 6 元", "collected":"茶饮已领取 · 沿铺带送往交接架", "paid":"茶饮已签收 · 配送收入 +6 元",
}

func setup(world: Node3D, configured_stops: Array = [], configured_job: Dictionary = {}) -> void:
	game=world
	job=configured_job if not configured_job.is_empty() else (SHANCHENG if configured_stops.is_empty() else RIVERSIDE_TEA)
	if configured_stops.is_empty():
		var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
		stops=layout.public_stops
	else:
		stops=configured_stops
	sender=register_stop(0,job.sender,func():return available(),func():pick_up())
	receiver=register_stop(1,job.receiver,func():return stage==Stage.CARRYING,func():deliver())
	parcel=preload("res://scripts/takeaway_bag.gd").new()
	add_child(parcel)
	parcel.ticket.text=job.ticket
	delivered_parcel=preload("res://scripts/takeaway_bag.gd").new()
	add_child(delivered_parcel)
	delivered_parcel.ticket.text=job.receipt
	rest_parcel()

func register_stop(index: int, title: String, allowed: Callable, action: Callable) -> Node3D:
	var p: Array=stops[index].target
	var target: Node3D=game._target(str(job.id)+"."+str(index),Vector3(p[0],p[1],p[2]),
		func():return job.pickup if index==0 else job.dropoff,allowed,action,self)
	var label:=Label3D.new()
	label.font=load("res://assets/district_500/district_signs.otf")
	label.text=title
	label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size=32
	label.pixel_size=.006 if job.id=="shancheng" else .0032
	label.outline_size=5
	label.visibility_range_end=22.
	target.add_child(label)
	label.position.y=.62
	return target

func available() -> bool:
	if stage==Stage.CARRYING or game.riding() or (game.lesson and game.lesson.step!=game.lesson.Step.DONE):return false
	if game.public_handoff_in_progress():return false
	if game.order not in [game.Order.AVAILABLE,game.Order.DELIVERED]:return false
	return (not game.lunch or not (game.lunch.active or game.lunch.preview)) and (not game.passage or (game.passage.stage==game.passage.Stage.IDLE and not game.passage.offered))

func rest_parcel() -> void:
	var completed: Array=stops[1].target
	delivered_parcel.global_position=Vector3(completed[0],stops[1].get("parcel_y",completed[1]-.066),completed[2])
	delivered_parcel.visible=stage==Stage.DELIVERED
	var p: Array=stops[0].target
	parcel.global_position=Vector3(p[0],stops[0].get("parcel_y",p[1]-.066),p[2])

func pick_up() -> void:
	if not available():return
	stage=Stage.CARRYING
	delivered_parcel.hide()
	game._say(job.collected)
	if game.lesson:game.lesson._save()

func deliver() -> void:
	if stage!=Stage.CARRYING:return
	stage=Stage.DELIVERED
	rest_parcel()
	game.delivered_count+=1
	game.earnings+=int(job.reward)
	game._say(job.paid)
	if game.lesson:game.lesson._save()

func _process(_dt: float) -> void:
	if stage==Stage.CARRYING and parcel:
		var hand: Vector3=game.free_wrist.global_position if game.free_wrist else game.actor.body.to_global(Vector3(.30,.88,-.13))
		parcel.global_position=hand-Vector3.UP*.32
		parcel.rotation.y=game.actor.body.rotation.y

func panel() -> String:
	if stage==Stage.CARRYING:return job.carrying
	if stage==Stage.DELIVERED and game.actor.body.global_position.distance_to(receiver.global_position)<12.:
		return job.done
	if available() and game.actor.body.global_position.distance_to(sender.global_position)<14.:
		return job.ready
	return ""
