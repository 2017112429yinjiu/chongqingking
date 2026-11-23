extends SceneTree
func _initialize():call_deferred("run")
func run():
	var dir:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/road_shift/resume")
	var rows:Array=[]
	for item in [["legacy_after_first",6,null,1,8],["third_at_rack",5,2,2,16],["finished",6,2,3,24]]:
		var file:=dir.path_join(str(item[0])+".cfg")
		var cfg:=ConfigFile.new()
		cfg.set_value("shift","step",item[1])
		if item[2]!=null:cfg.set_value("shift","round",item[2])
		cfg.set_value("shift","deliveries",item[3])
		cfg.set_value("shift","earnings",item[4])
		cfg.set_value("shift","door_shown",true)
		cfg.set_value("shift","answered",true)
		cfg.save(file)
		var scene=load("res://main.tscn").instantiate()
		root.add_child(scene)
		while not scene.gameplay:await physics_frame
		var game:Node3D=scene.gameplay
		var l:=preload("res://scripts/day_one.gd").new()
		game.add_child(l)
		game.lesson=l
		l.setup(game,file)
		for tick in 50:await physics_frame
		var ok:bool=game.earnings==item[4] and game.delivered_count==item[3] and game.actor.body.is_on_floor()
		match item[0]:
			"legacy_after_first":ok=ok and l.round_index==1 and l.step in [l.Step.RETURN,l.Step.TO_SHOP] and is_instance_valid(l.mentor)
			"third_at_rack":ok=ok and l.round_index==2 and l.recipient_answered and l.collection().bay_targets[1].available() and game.order==game.Order.CARRYING
			"finished":ok=ok and l.step==l.Step.DONE and not l.mentor.escort and game.shop.available()
		rows.append({"case":item[0],"pass":ok,"order":l.round_index+1,"step":l.Step.keys()[l.step],"earnings":game.earnings,"on_ground":game.actor.body.is_on_floor()})
		scene.queue_free()
		await process_frame
		await physics_frame
	print("SHIFT_RESUME ",JSON.stringify(rows))
	FileAccess.open(dir.path_join("resume.json"),FileAccess.WRITE).store_string(JSON.stringify(rows,"\t"))
	quit(0 if rows.all(func(row):return row["pass"]) else 2)
