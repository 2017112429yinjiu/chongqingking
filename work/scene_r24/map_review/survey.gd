extends "../../scene_r24/outer_neighborhood/survey.gd"

const Inventory = preload("inventory.gd")
var views:=[]
var cam:Camera3D

func write_json(file: String, data: Variant) -> void:
	var f:=FileAccess.open(output.path_join(file),FileAccess.WRITE)
	assert(f!=null)
	f.store_string(JSON.stringify(data))

func vec(a: Array) -> Vector3:return Vector3(a[0],a[1],a[2])
func enu(a: Array) -> Vector3:return Vector3(a[0],a[2],-a[1])

func picture(key:String, title:String, eye:Vector3, target:Vector3, fov:=70.) -> void:
	cam.global_position=eye
	cam.look_at(target)
	cam.fov=fov
	await process_frame
	RenderingServer.force_draw(false,1./60.)
	var path:=output.path_join(key+".jpg")
	assert(root.get_texture().get_image().save_jpg(path,.84)==OK)
	var cast:=PhysicsRayQueryParameters3D.create(eye,eye+eye.direction_to(target)*8,1)
	var hit:=scene.get_world_3d().direct_space_state.intersect_ray(cast)
	views.append({"key":key,"title":title,"eye":Inventory.new().xyz(eye),"target":Inventory.new().xyz(target),
		"fov":fov,"first_collision":str(scene.get_path_to(hit.collider)) if hit else "",
		"distance_m":snappedf(eye.distance_to(hit.position),.01) if hit else null})

func plots(data:Dictionary) -> void:
	for p: Dictionary in data.plots:
		var key:="plot_%02d_"%int(p.plot_id)
		var f:float=-p.depth*.5
		var door:float=p.door_u
		var side:float=clampf(p.width*.31,2.0,6.0)
		var pos:=world(p,door-side,f-5.7,0)
		var foot:=public_floor([pos.x,-pos.z],p.height+.35)
		if not foot.is_finite():foot=pos
		await picture(key+"street",str(p.name),foot+Vector3.UP*1.60,world(p,door,f,1.84))
		await picture(key+"hall",str(p.name),world(p,door+.16,f+.64,1.60),world(p,door-.14,-f-.8,1.3))
		if p.has("room"):
			var r:Dictionary=p.room
			await picture(key+"room",str(r.use),world(p,r.jamb_u,r.door_v,1.57),world(p,r.inside_u,f+1.25,1.02))
		if p.has("court"):
			var c:Dictionary=p.court
			await picture(key+"upper","院楼",world(p,c.room_u,c.room_v,c.upper_m+1.58),world(p,c.bed_local[0],c.bed_local[1],c.upper_m+.55))
		if p.has("repair_court"):
			var r:Dictionary=p.repair_court
			await picture(key+"yard","修理院回望",enu(r.court)+Vector3.UP*1.58,enu(r.rear)+Vector3.UP*1.28)

func registered() -> void:
	var lane:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
	for b:Dictionary in lane.buildings:
		var center:=Vector3.ZERO
		for p:Array in b.wall_base_corners:center+=Vector3(p[0],b.floor_z,-p[1])*.25
		var door:=enu(b.door)
		var inside:=door.direction_to(center)
		var key:="mapped_"+str(b.osm).replace("@","_")
		await picture(key+"_front",b.osm,door-inside*4.3+Vector3.UP*1.59,center+Vector3.UP*1.36)
		await picture(key+"_inside",b.osm,door+inside*.85+Vector3.UP*1.59,center+Vector3.UP*1.10)
	for key:String in ["primary","branch"]:
		var path:Array=lane[key]
		for i in range(0,path.size()-1,3):
			await picture("lane_%s_%02d"%[key,i],key,enu(path[i])+Vector3.UP*1.6,enu(path[i+1])+Vector3.UP*1.22)

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	var art:="--art-entry" in OS.get_cmdline_user_args()
	var entry:String="res://main.tscn" if art else ProjectSettings.get_setting("application/run/main_scene")
	scene=load(entry).instantiate()
	root.add_child(scene)
	current_scene=scene
	for i in 1600:
		if scene.explorer and (art or scene.gameplay):break
		await physics_frame
	assert(scene.explorer!=null)
	await frames(36)
	var inventory:=Inventory.new()
	write_json("nodes.json",inventory.collect(scene))
	if not art:write_json("ground.json",inventory.ground_grid(scene))
	if DisplayServer.get_name()!="headless":
		RenderingServer.render_loop_enabled=false
		scene.hud.hide()
		cam=Camera3D.new()
		scene.add_child(cam)
		cam.make_current()
		for key:String in scene.VIEW_NAMES:
			var v:Dictionary=scene.config.views[key]
			await picture("core_"+key,str(v.get("title",key)),vec(v.position),vec(v.target),float(v.get("fov",65.)))
		if not art:
			await plots(JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json")))
			await registered()
	write_json("views.json",{"entry":entry,"configured_cameras":scene.VIEW_NAMES,"views":views})
	quit(0)
