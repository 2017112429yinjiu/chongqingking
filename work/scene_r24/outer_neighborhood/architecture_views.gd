extends "../../scene_r24/outer_neighborhood/survey.gd"

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	RenderingServer.render_loop_enabled=false
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.get("gameplay"): await physics_frame
	await frames(24)
	scene.hud.hide()
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	for p: Dictionary in layout.plots:
		if p.name.is_empty() and int(p.plot_id) not in [3,4,5]: continue
		var label: String=SHORT.get(p.name,"home_%02d"%int(p.plot_id))
		var f: float=-p.depth*.5
		var u: float=p.door_u
		var front_xy:=world(p,-p.width*.51,f-7.6,0)
		var foot:=public_floor([front_xy.x,-front_xy.z],p.height+.28)
		if foot.is_finite():
			await shot(label+"_facade",foot+Vector3.UP*1.56,world(p,-p.width*.08,f+.1,3.68))
		if p.has("room"):
			var r: Dictionary=p.room
			await shot(label+"_inside",world(p,r.jamb_u,r.door_v,1.63),world(p,r.inside_u,f+1.32,.89))
		else:
			await shot(label+"_hall",world(p,u+.28,f+.73,1.64),world(p,u+2.05,-f-1.6,1.26))
			var c: Dictionary=p.court
			await shot(label+"_bed",world(p,c.room_u,c.room_v,c.upper_m+1.59),world(p,c.bed_local[0],c.bed_local[1],c.upper_m+.57))
	await shot("old_service",Vector3(-6.82,23.98,-12.58),Vector3(3.9,23.38,-12.50))
	await shot("old_overhang",Vector3(-4.16,17.5,28.83),Vector3(-1.17,16.32,28.82))
	quit()
