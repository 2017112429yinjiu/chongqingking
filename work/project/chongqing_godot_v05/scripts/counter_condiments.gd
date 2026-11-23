extends Node3D
## The rider adds a sealed side portion when the customer's ticket requests one.
enum State { NONE, ON_COUNTER, ADDING, PACKED }
const STATION := preload("res://assets/counter_r21/chilli_station.glb")
const PORTION := preload("res://assets/counter_r21/side_portion.glb")
const BASE := Vector3(.217,0,.625)
const INSIDE := Vector3(-.014,.156,.005)
var state:=State.NONE
var cup: Node3D
var bag: Node3D

func setup(npc: Node3D,food: Node3D) -> void:
	bag=food
	global_transform=npc.global_transform
	global_position.y=npc.food_end.y
	var crock:=STATION.instantiate() as Node3D
	add_child(crock)
	crock.position=Vector3(.298,0,.457)
	crock.rotation.y=-.26
	cup=PORTION.instantiate()
	add_child(cup)
	cup.hide()

func begin(requested: bool) -> void:
	if cup.get_parent()!=self:cup.reparent(self,false)
	cup.position=BASE
	cup.visible=requested
	state=State.ON_COUNTER if requested else State.NONE

func pack() -> void:
	if state!=State.ON_COUNTER:return
	state=State.ADDING
	# Lift clear of the worktop, cross above the lip, then settle on the bowl lid.
	var above:=to_local(bag.to_global(INSIDE+Vector3.UP*.230))
	var tween:=create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(cup,"position",BASE+Vector3.UP*.33,.23)
	tween.tween_property(cup,"position",above,.30)
	tween.tween_property(cup,"position",to_local(bag.to_global(INSIDE)),.24)
	tween.tween_callback(func():
		cup.reparent(bag,true)
		cup.position=INSIDE
		state=State.PACKED)
