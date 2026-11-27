extends "../../continuous_site_walk.gd"

const DATA := "res://assets/district_500/binjiang-70-73.json"
var plan: Dictionary
var plot: String
var baseline: bool

func site_plan() -> Dictionary:
	plot=preload("res://scripts/district_500.gd").binjiang_plot()
	baseline="--qa-without-binjiang" in OS.get_cmdline_user_args()
	plan=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var site: Dictionary=plan.public_routes[plot]
	var old := []
	for id: String in plan.public_routes:
		var original := "COL_Outer500_Frame_"+id
		old.append([original,scene.find_child(original,true,false)!=null])
	check("former_plot_frames",old.all(func(row: Array) -> bool: return row[1]==baseline),old)
	var named := []
	for node: Node in scene.find_children("*","MeshInstance3D",true,false):
		if "1128648941" in node.name or "704006726" in node.name:
			named.append(str(node.get_path()))
	check("one_registered_tower",baseline or scene.find_children("Binjiang_Tower_1128648941","MeshInstance3D",true,false).size()==1,named)
	var superseded := []
	for name: String in plan.get("retired_runtime_frontage",[]):
		var former := scene.find_child(name,true,false) as MeshInstance3D
		superseded.append([name,former!=null and former.is_visible_in_tree()])
	check("former_frontage_layers",superseded.size()==5 and superseded.all(func(row: Array)->bool: return row[1]==baseline),superseded)
	var support := []
	for station:Array in site.stations:
		for x: float in [-.55,0.,.55]:
			var p := [station[0]+x+.017,station[1]+.015]
			var contacts := column(p)
			support.append({"en":p,"hits":contacts,"walk":contacts.any(func(h: Array)->bool:
				return h[0]=="COL_Binjiang_Walk_"+plot and h[2]>.78)})
	check("public_walk_contact",baseline or support.all(func(row: Dictionary)->bool: return row.walk),support)
	var start: Array=site.stations[0]
	var target: Array=site.stations[-1]
	return {"id":"binjiang_"+plot,"stations":site.stations,"destination_y":site.destination_game_m,
		"street_focus":[target[0],target[1],site.destination_game_m+1.6],
		"return_focus":[start[0],start[1],site.start_ground_m+1.63]}

func eye_frame(label: String,focus: Variant) -> void:
	if label=="street":
		if "--binjiang-all-views" in OS.get_cmdline_user_args():
			for id: String in plan.public_routes:
				await fixed_view(plan.public_routes[id].shot)
		else:
			await fixed_view(plan.public_routes[plot].shot)
	elif label=="inside_look_back":
		await super.eye_frame(label,focus)

func leg_without_placement(label: String,goals: Array) -> Dictionary:
	var result := await super.leg_without_placement(label,goals)
	if not result.pass and graphics:
		var stop: Array=plan.public_routes[plot].stations[-1]
		var eye_height: float=scene.explorer.camera.global_position.y
		await super.eye_frame("blocked-"+plot,[stop[0],stop[1],eye_height])
	return result

func fixed_view(frame: Array) -> void:
	var eye: Array=frame[1]
	var focus: Array=frame[2]
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.position=Vector3(eye[0],eye[2],-eye[1])
	camera.look_at(Vector3(focus[0],focus[2],-focus[1]))
	camera.fov=frame[3]
	camera.make_current()
	await process_frame
	RenderingServer.force_draw(false,1.0/60.0)
	var image:=root.get_texture().get_image()
	var file: String=frame[0]+".png"
	check("render_"+frame[0],image.save_png(output.path_join(file))==OK,file)
	view_positions.append({"image":file,"eye_enu":eye,"focus_enu":focus,"vfov":camera.fov,"pixels":str(image.get_size())})
	scene.explorer.camera.make_current()
	camera.queue_free()
