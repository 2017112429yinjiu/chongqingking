extends "../../scene_r24/day_one/verify.gd"
var probes:=0
var gaps:Array=[]
var low_heads:Array=[]
var min_head:=8.
func sample_floor(p:Vector3, tolerance:float)->float:
	probes+=1
	var space:=game.get_world_3d().direct_space_state as PhysicsDirectSpaceState3D
	var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.35,p-Vector3.UP*.58,1)
	var hit:=space.intersect_ray(q)
	if hit.is_empty():
		gaps.append([str(p),"absent"])
		return -99.
	var floor_p:Vector3=hit.position
	if absf(floor_p.y-p.y)>tolerance:gaps.append([str(p),floor_p.y])
	q.from=floor_p+Vector3.UP*.09
	q.to=floor_p+Vector3.UP*8
	var ceil_hit:=space.intersect_ray(q)
	if not ceil_hit.is_empty():
		var h:float=ceil_hit.position.y-floor_p.y
		min_head=minf(h,min_head)
		if h<1.98:low_heads.append([str(floor_p),h,str(ceil_hit.collider.get_parent().name)])
	return floor_p.y
func verify()->void:
	output=preload("res://scripts/qa_context.gd").directory()
	scene=load("res://main.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	game=scene.gameplay
	await frames(20)
	for step in 20:
		for offset:float in [-.65,0.,.65]:
			sample_floor(Vector3(-84.90+offset,17.12+(step+1)*.17,10.40+(step+.5)*.29),.018)
			sample_floor(Vector3(-82.55+offset,20.52+(step+1)*.17,16.20-(step+.5)*.29),.018)
	for i in 55:
		for z:float in [13.81,14.37,14.91]:
			sample_floor(Vector3(-78.65+i*.25,23.92,z),.018)
	for i in 6:
		for z:float in [13.81,14.37,14.91]:
			sample_floor(Vector3(-65+(i+.5)*.30,23.92-(i+1)*.17,z),.018)
	var max_seam:=0.
	for x:float in [-85.84,-84.8,-83.93]:
		var previous:float=0.
		for i in 22:
			var y:=sample_floor(Vector3(x,17.12,7.85+i*.085),.32)
			if i>0:max_seam=maxf(max_seam,absf(previous-y))
			previous=y
	check("all_walk_surfaces",gaps.is_empty(),gaps)
	check("overhead_clearance",low_heads.is_empty(),low_heads)
	check("joined_alley_threshold",max_seam<.065,max_seam)
	FileAccess.open(output.path_join("section.json"),FileAccess.WRITE).store_string(JSON.stringify({"probes":probes,"min_headroom_m":min_head,"checks":checks},"\t"))
	quit(2 if ever_failed else 0)
