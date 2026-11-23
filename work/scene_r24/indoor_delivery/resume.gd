extends SceneTree
func _initialize()->void:call_deferred("verify")
func verify()->void:
	var out:=preload("res://scripts/qa_context.gd").directory()
	var rows:Array=[]
	for phase:String in ["last_mile","knocked","after_door","completed"]:
		var cfg:=out.path_join(phase+".cfg")
		var source:String=""
		for arg in OS.get_cmdline_user_args():
			if arg.begins_with("--checkpoints="):source=arg.trim_prefix("--checkpoints=")
		if DirAccess.copy_absolute(source.path_join(phase+".cfg"),cfg)!=OK:quit(3);return
		var scene=load("res://main.tscn").instantiate()
		root.add_child(scene)
		while not scene.gameplay:await physics_frame
		var game:Node3D=scene.gameplay
		var l:=preload("res://scripts/day_one.gd").new()
		game.add_child(l)
		game.lesson=l
		l.setup(game,cfg)
		for k in 45:await physics_frame
		var foot:Vector3=game.actor.body.global_position
		var ok:bool=game.actor.body.is_on_floor()
		match phase:
			"last_mile":ok=ok and l.round_index==0 and not l.demo.door_shown and game.earnings==0
			"knocked":ok=ok and foot.distance_to(l.Unit.LANDING)<.35 and l.demo.student_knocked and l.demo.door_shown and not l.demo.student_hooked and game.earnings==0 and l.demo.walker.global_position.y>19.7
			"after_door":ok=ok and l.round_index==1 and game.earnings==8 and l.step in [l.Step.RETURN,l.Step.TO_SHOP]
			"completed":ok=ok and l.step==l.Step.DONE and game.earnings==24 and l.mentor.escort==false and game.destination.global_position.distance_to(l.Unit.DOOR_POINTS[0])<.05
		rows.append({"case":phase,"pass":ok,"feet":str(foot),"earned":game.earnings,"step":l.step})
		scene.queue_free()
		await process_frame
		await physics_frame
	FileAccess.open(out.path_join("resume.json"),FileAccess.WRITE).store_string(JSON.stringify(rows,"\t"))
	print("UNIT_RESUME ",rows)
	quit(0 if rows.all(func(row):return row["pass"]) else 2)
