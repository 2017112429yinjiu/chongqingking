extends "../../scene_r24/outer_neighborhood/survey.gd"

var recording := false
var saved_frames := 0
var physics_ticks := 0

func record_tick() -> void:
	while recording:
		await physics_frame
		if not recording: break
		if physics_ticks%9==0:
			RenderingServer.force_draw(false,1.0/60.0)
			var img:=root.get_texture().get_image()
			img.save_jpg(output.path_join("walk_%03d.jpg"%saved_frames),.88)
			saved_frames+=1
		physics_ticks+=1

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	var graphics:=DisplayServer.get_name()!="headless"
	if graphics: RenderingServer.render_loop_enabled=false
	scene=load(ProjectSettings.get_setting("application/run/main_scene")).instantiate()
	root.add_child(scene)
	current_scene=scene
	for i in 1800:
		if scene.get("gameplay"):break
		await physics_frame
	await frames(32)
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var p: Dictionary
	for plot: Dictionary in layout.plots:
		if plot.name=="照相巷便民市场":p=plot
	if not check("exploration_from_normal_scene",scene.get("gameplay")!=null and scene.gameplay.lesson==null and not p.is_empty()):
		quit(2)
		return
	var f: float=-p.depth/2
	var c: Dictionary=p.court
	var u: float=p.door_u
	var h: float=c.upper_m
	var actor=scene.explorer
	var nominal:=world(p,-p.width*.27,f-1.92,.05)
	check("market_threshold_spawn",actor.body.global_position.distance_to(nominal)<.35,str(actor.body.global_position))
	var points: Array=[world(p,u,f-1.96,.06),world(p,u,f+.94,.06),world(p,u,-f+.62,.14),
		world(p,c.stair_u,-f+.62,.14),world(p,c.stair_u,c.landing_v,h+.045),
		world(p,c.room_u,c.landing_v,h+.045),world(p,c.room_u,c.room_v,h+.045)]
	if graphics:
		recording=true
		record_tick()
	var take:=await WalkTest._walk(scene,points,"market_to_201")
	recording=false
	check("uninterrupted_market_to_201",take["pass"],take)
	check("upstairs_height",absf(actor.body.global_position.y-p.height-h)<.18,str(actor.body.global_position))
	var workers: Array=[]
	for name in ["OuterMarketSeller","OuterRepairWorker"]:
		var person:=scene.find_child(name,true,false) as Node3D
		if person==null: continue
		var player:=person.find_child("AnimationPlayer",true,false) as AnimationPlayer
		var pos:=person.global_position
		var ray:=PhysicsRayQueryParameters3D.create(pos+Vector3.UP*.14,pos-Vector3.UP*.22,1)
		var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
		workers.append({"name":name,"clip":str(player.current_animation),"foot_origin_gap_m":pos.y-hit.position.y if not hit.is_empty() else null})
	check("local_worker_clips_and_floor",workers.size()==2 and workers.all(func(row):return row.foot_origin_gap_m!=null and absf(row.foot_origin_gap_m)<.04 and not row.clip.is_empty()),workers)
	FileAccess.open(output.path_join("market_entry.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"physics_hz":Engine.physics_ticks_per_second,"ticks_per_image":9,"images":saved_frames},"  "))
	quit(2 if ever_failed else 0)
