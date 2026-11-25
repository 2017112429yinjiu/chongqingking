extends "../../scene_r24/outer_neighborhood/shared_paths.gd"

var trace:=[]
var active:=false

func sample(body: CharacterBody3D) -> void:
	while active:
		await physics_frame
		var collisions:=[]
		for j in body.get_slide_collision_count():
			var contact:=body.get_slide_collision(j)
			collisions.append({"mesh":str(contact.get_collider().get_parent().name),"at":str(contact.get_position()),"normal":str(contact.get_normal())})
		if trace.size()<1400:trace.append({"at":str(body.global_position),"hits":collisions})

func trial(label: String,points: Array,both: bool=true) -> void:
	if label!="lane_53_4" or not "--full-sequence" in OS.get_cmdline_user_args():
		await super.trial(label,points,both)
		return
	active=true
	sample(scene.explorer.body)
	await super.trial(label,points,both)
	active=false
	FileAccess.open(output.path_join("contact_sequence.json"),FileAccess.WRITE).store_string(JSON.stringify(trace))

func verify() -> void:
	if "--full-sequence" in OS.get_cmdline_user_args():
		await super.verify()
		return
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(16)
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for lane: Dictionary in layout.lanes:
		if lane.type!="shared":continue
		var a:Dictionary=layout.plots[lane.plots[0]]
		var b:Dictionary=layout.plots[lane.plots[1]]
		if a.plot_id!=53 or b.plot_id!=4:continue
		var pa:=public_floor(lane.points[0],a.height)
		var pb:=public_floor(lane.points[1],b.height)
		var points:=paved_route(pa,pb,layout.planting)
		active=true
		sample(scene.explorer.body)
		await trial("lane_53_4",points)
		active=false
		var info={"starts":[str(pa),str(pb)],"trace":trace,"walks":checks}
		FileAccess.open(output.path_join("contact.json"),FileAccess.WRITE).store_string(JSON.stringify(info))
		quit(2 if ever_failed else 0)
		return
	quit(2)
