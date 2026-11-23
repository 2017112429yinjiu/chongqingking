extends SceneTree
func _initialize()->void:call_deferred("survey")

func survey()->void:
	var game=load("res://main.tscn").instantiate()
	root.add_child(game)
	while game.gameplay==null:await physics_frame
	var folder:String=OS.get_cmdline_user_args()[-1]
	var sites:Array=JSON.parse_string(FileAccess.get_file_as_string(folder+"/legacy_grate_sites.json"))
	var space:PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
	var count:=0
	for site:Dictionary in sites:
		var p:=Vector3(float(site.position[0]),float(site.bar_top),float(site.position[2]))
		var gaps:Array=[]
		var floors:Dictionary={}
		for dx in [-.165,0.,.165]:
			for dz in [-.125,0.,.125]:
				var q:=p+Vector3(dx,0,dz)
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(q+Vector3.UP*1.0,q-Vector3.UP*1.0,1))
				if hit.is_empty():continue
				gaps.append(q.y-hit.position.y)
				var name_key:String=str(hit.collider.get_parent().name)
				floors[name_key]=int(floors.get(name_key,0))+1
		site["floors"]=floors
		site["samples"]=gaps.size()
		if gaps.is_empty():site["requires_review"]=true
		else:
			site["bar_top_above_collision_min_m"]=gaps.min()
			site["bar_top_above_collision_max_m"]=gaps.max()
			site["requires_review"]=gaps.size()!=9 or gaps.min()<-.02 or gaps.max()>.055
		if site.requires_review:count+=1
	var report:={"total":sites.size(),"flagged":count,"sites":sites,"scope":"Legacy seven-bar estate fittings only. Outliers prioritise visual inspection; collision measurements alone do not establish an art defect."}
	preload("res://scripts/qa_context.gd").decorate(report,game)
	FileAccess.open(folder+"/legacy_grate_contacts.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("EAST17_GRATE_SURVEY ",sites.size()," ",count)
	quit(0 if sites.size()>0 else 3)
