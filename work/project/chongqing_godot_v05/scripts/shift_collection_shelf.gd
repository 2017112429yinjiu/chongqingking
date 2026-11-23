extends Node3D
## A neighbourhood collection point. The shelf surface, label and interaction
## use the same local coordinates; each foot extends to the actual sloping street.
var slots: Array[Vector3] = []
var bay_targets: Array[Node3D] = []
var controller: Node3D
var title: String
var call_point:=Vector3.ZERO

func install(lesson:Node3D, at:Vector3, caption:String, index:int) -> void:
	controller=lesson
	title=caption
	var game:Node3D=lesson.game
	global_position=game._grounded(at)
	var frame:=StandardMaterial3D.new()
	frame.albedo_color=Color("394a46")
	frame.roughness=.74
	frame.metallic=.31
	var plank:=StandardMaterial3D.new()
	plank.albedo_texture=preload("res://assets/chongqing_district_wood_table_worn_diff_2k.jpg")
	plank.roughness=.88
	for x:float in [-.67,.67]:
		for z:float in [-.20,.20]:
			var foot:Vector3=to_local(game._grounded(to_global(Vector3(x,0,z))))
			var post_top:=.975 if z<0. else .8125
			var height:=post_top-foot.y+.01
			piece(Vector3(x,post_top-height*.5,z),Vector3(.035,height,.035),frame)
	piece(Vector3(0,.835,0),Vector3(1.41,.045,.49),plank)
	piece(Vector3(0,.39,0),Vector3(1.38,.028,.43),plank)
	piece(Vector3(0,.779,.231),Vector3(1.38,.067,.026),frame)
	piece(Vector3(0,.921,-.21),Vector3(1.4,.16,.035),frame)
	label(caption,Vector3(0,.926,-.184),.00135)
	if index==2:
		piece(Vector3(-.62,1.02,-.15),Vector3(.045,.36,.04),frame)
		piece(Vector3(-.62,1.14,-.11),Vector3(.16,.22,.068),frame)
		var enamel:=StandardMaterial3D.new()
		enamel.albedo_color=Color("c78355")
		piece(Vector3(-.62,1.12,-.064),Vector3(.064,.061,.026),enamel)
		call_point=to_global(Vector3(-.62,1.12,-.048))
		var call_button:Node3D=game._target("shift.court.call",call_point+Vector3.BACK*.04,
			func():return "按取餐架呼叫键，报 006 号",
			func():return lesson.round_index==2 and lesson.step==lesson.Step.LAST_METRES and lesson.demo.door_shown and not lesson.recipient_answered,
			func():lesson.notify_recipient())
		call_button.radius=.95
	for side in 2:
		var x:float=[-.39,.39][side]
		slots.append(to_global(Vector3(x,.858,.035)))
		label(["甲","乙"][side],Vector3(x,.779,.2455),.00135)
		var target:Node3D=game._target("shift.shelf.%d.%d"%[index,side],slots[side]+Vector3.UP*.10,
			func():return "放在%s位" % ["甲","乙"][side],
			func():return lesson.round_index==index and lesson.step==lesson.Step.LAST_METRES and lesson.demo.door_shown and (index==1 or lesson.recipient_answered) and game.order==game.Order.CARRYING,
			func():lesson.place_on_shelf(side))
		target.radius=.93
		bay_targets.append(target)
	var body:=StaticBody3D.new()
	add_child(body)
	var collider:=CollisionShape3D.new()
	var shape:=BoxShape3D.new()
	shape.size=Vector3(1.41,.97,.49)
	collider.shape=shape
	body.add_child(collider)
	collider.position.y=.47

func piece(at:Vector3,size:Vector3,mat:Material) -> void:
	var part:=MeshInstance3D.new()
	var box:=BoxMesh.new()
	box.size=size
	part.mesh=box
	part.material_override=mat
	add_child(part)
	part.position=at

func label(words:String,at:Vector3,scale_m:float) -> void:
	var text:=Label3D.new()
	text.text=words
	text.font=preload("res://assets/fonts/first_shift.otf")
	text.font_size=36
	text.pixel_size=scale_m
	text.modulate=Color("e6dfc4")
	text.outline_size=0
	add_child(text)
	text.position=at
