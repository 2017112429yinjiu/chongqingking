extends SceneTree
func _initialize()->void:call_deferred("run")

func run()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var block=game.street_block
	block.set_physics_process(false)
	var original:Array=block.tracks.duplicate()
	var rows=[];var failed=[]
	for key in block.return_corridors:
		for end_name in ["start","end"]:
			var t:Dictionary={}
			for actor in original:
				if actor.route==key:t=actor;break
			if t.is_empty():failed.append(key);continue
			block.tracks.clear();block.tracks.append(t)
			var limit:float=block.routes[key].get_baked_length()
			t.sign=-1. if end_name=="start" else 1.
			t.d=.18 if end_name=="start" else limit-.18
			t.turn_from=0.;t.debt=0.;t.v=t.pace;t.wait=0.;t.errand_phase=1;t.stopped=false
			t.animation.play(t.walk_clip);block._pose(t,0.,true)
			game.explorer.camera.global_position=t.node.global_position+Vector3(1.,1.65,2.2)
			var last:Vector3=t.node.position
			var largest:=0.;var idle_frames:=0;var resumed:=false;var jumped:=0.
			var signed_before:float=t.sign
			var greatest_yaw:=0.;var prev_basis:Basis=t.node.basis
			for tick in 480:
				block._physics_process(1./60.)
				var point:Vector3=t.node.position
				var step:=Vector2(point.x-last.x,point.z-last.z).length()
				largest=maxf(largest,step)
				if t.sign!=signed_before and jumped==0.:jumped=step
				if t.wait>0. and t.stopped and t.animation.current_animation==t.standing:
					idle_frames+=1
					greatest_yaw=maxf(greatest_yaw,prev_basis.get_rotation_quaternion().angle_to(t.node.basis.get_rotation_quaternion()))
				if idle_frames and t.sign!=signed_before and t.wait==0. and not t.stopped and t.animation.current_animation==t.walk_clip and absf(t.d-t.turn_station)>1.0:resumed=true
				prev_basis=t.node.basis;last=point
			var ok:bool=largest<.055 and idle_frames>50 and resumed and greatest_yaw<deg_to_rad(2.45)
			if not ok:failed.append(key+"_"+end_name)
			rows.append({"route":key,"end":end_name,"largest_horizontal_frame":largest,"reversal_frame":jumped,"standing_frames":idle_frames,"max_turn_degrees_per_frame":rad_to_deg(greatest_yaw),"walking_resumed":resumed,"pass":ok})
	block.tracks.assign(original)
	var report={"passed":failed.is_empty() and rows.size()==10,"failures":failed,"ends":rows}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	var dest=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(dest)
	FileAccess.open(dest+"/pedestrian_turns.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("COURT14_TURNS ",report.passed," ",failed)
	quit(0 if report.passed else 3)

