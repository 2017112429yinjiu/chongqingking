extends "../../scene_r24/day_one/verify.gd"
# Each circuit has one initial placement. The mentor then steers to the road end and back.
const ROADS = [0,3,4,5,9,18,19,23,24,25,26,27,28,29]
const LABELS = ["南区路", "中兴路", "东侧弯道", "北界横街", "临江路", "坡下横街", "南侧横巷", "墙边支路", "中央梯坎", "西侧住区", "小院入口", "上院步道", "旧校路", "东照相巷"]
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	lesson=game.lesson
	lesson.set_physics_process(false)
	bike=lesson.mentor
	if not lesson.demo.walker.mounted:
		lesson.demo.walker.board()
		await frames(75)
	bike.escort=false
	bike.articulation.set_occupied(true)
	if not check("instructor_in_saddle",lesson.demo.walker.mounted and bike.articulation.is_ancestor_of(lesson.demo.walker.human)):
		quit(2);return
	var survey:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../../scene_r24/district_age/road_queries.json"))
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.current=true
	RenderingServer.render_loop_enabled=false
	var report:=[]
	for n in ROADS.size():
		var points:=PackedVector3Array()
		for s:Array in survey.sections:
			if int(s[0])!=ROADS[n] or s[1]!=1 or s[4]==null or absf(s[2])>98.5 or absf(s[3])>98.5:continue
			var p:=Vector3(s[2],s[4],s[3])
			if points.is_empty() or points[-1].distance_to(p)>2.0:points.append(p)
		if points.size()<3:continue
		var dir:Vector3=points[1]-points[0]
		bike.global_position=points[0]+Vector3.UP*.18
		bike.rotation=Vector3(0,atan2(-dir.x,-dir.z),0)
		bike.velocity=Vector3.ZERO
		bike.speed=0
		bike.parked=true
		bike.last_obstacle={}
		await frames(20)
		var result:={"road":LABELS[n],"id":ROADS[n],"legs":[]}
		for leg in 2:
			var route:=points.duplicate()
			if leg:route.reverse()
			# Turn on the spot at the terminal as one would remount facing back along the lane.
			if leg:
				var back:=route[1]-route[0]
				bike.rotation.y=atan2(-back.x,-back.z)
			bike.parked=false
			bike.guide_to(route.slice(1))
			var last:=bike.global_position
			var last_index:=-1
			var still:=0
			var meters:=0.
			var samples:=[]
			for tick in 24000:
				await physics_frame
				var at:=bike.global_position
				meters+=Vector2(at.x-last.x,at.z-last.z).length()
				last=at
				if tick%45==0:samples.append([snappedf(at.x,.01),snappedf(at.y,.01),snappedf(at.z,.01)])
				if tick==180 and leg==0 and DisplayServer.get_name()!="headless":
					camera.global_position=at+bike.global_basis.z*2.7+Vector3.UP*2.15
					camera.look_at(at-bike.global_basis.z*.8+Vector3.UP*.98)
					camera.make_current()
					camera.reset_physics_interpolation()
					camera.force_update_transform()
					await frames(3)
					await capture("%02d_%d"%[n+1,ROADS[n]])
				if bike.arrived:break
				if last_index!=bike.next_point:still=0;last_index=bike.next_point
				else:still+=1
				if still>440:break
			result.legs.append({"completed":bike.arrived,"metres":snappedf(meters,.01),"reached":bike.next_point,"count":bike.path.size(),"samples":samples,"obstacle":bike.last_obstacle.duplicate(true)})
			if not bike.arrived:break
		report.append(result)
		print("PATROL ",ROADS[n]," ",result.legs.size()," ",result.legs[-1].completed)
		FileAccess.open(output.path_join("patrol.json"),FileAccess.WRITE).store_string(JSON.stringify(report))
	for road:Dictionary in report:
		var legs:Array=road.legs
		check("both_directions_%s"%road.id,legs.size()==2 and legs.all(func(leg):return leg.completed))
	check("all_requested_roads",report.size()==ROADS.size())
	quit(2 if ever_failed else 0)
