extends SceneTree
func _initialize()->void:call_deferred("review")
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])

func joint(rec:Dictionary,key:String)->Vector3:
	var sk:Skeleton3D=rec.bones
	var idx:=sk.find_bone("Bip01 "+key)
	if idx==-1:idx=sk.find_bone("Bip01_"+key.replace(" ","_"))
	assert(idx!=-1,key)
	return sk.to_global(sk.get_bone_global_pose(idx).origin)

func review()->void:
	var host=load("res://main.tscn").instantiate()
	root.add_child(host)
	while host.gameplay==null:await physics_frame
	for i in 3:await physics_frame
	var scene=host.get_node("City/CourtyardLife14")
	var space=host.get_world_3d().direct_space_state
	scene.set_physics_process(false)
	var study:String=OS.get_cmdline_user_args()[-1]
	var output=preload("res://scripts/qa_context.gd").directory("res://verification_r24/build14")
	var errors=[];var contact_report={};var hand_report={};var props_max:=0.;var feet_misses=[]
	for spec in scene.layout.actors:
		var role:String=spec.role
		var record:Dictionary=scene.residents[role];var person:Node3D=record.person
		var measured_in:=study+"/kitchen" if role=="greens" and host.art_profile.get("fitted_kitchen_r24",false) else study
		var measurements:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(measured_in+"/"+role+"_contacts.json"))
		var worst_pose:=0.;var max_touch:=0.;var min_touch:=10.;var touch_frames:=0
		var drift:=0.;var stage={};var tested:=0;var fitted:=[]
		for marked in measurements.poses:
			var time:float=marked.t
			scene.update_at(fposmod(time-(2. if role=="greens" else 0.),16.),true)
			record.bones.force_update_all_bone_transforms()
			for name_of_bone:String in marked.marks:
				var delta=joint(record,name_of_bone).distance_to(person.to_global(vec(marked.marks[name_of_bone])))
				if not stage.has(name_of_bone):stage[name_of_bone]=0.
				stage[name_of_bone]=maxf(delta,stage[name_of_bone])
				worst_pose=maxf(worst_pose,delta)
			if time==0.:
				for key in ["seat","left","right"]:
					var name_of_bone="Pelvis" if key=="seat" else ("L Foot" if key=="left" else "R Foot")
					# Transport the measured skinned-sole / trouser contact by the actual in-engine joint displacement.
					var offset=person.global_basis*(vec(measurements.contacts[key])-vec(marked.marks[name_of_bone]))
					var point=joint(record,name_of_bone)+offset
					var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.065,point-Vector3.UP*.11,1))
					fitted.append({"key":key,"error":hit.position.y-point.y if hit else 9.,"body":str(hit.collider.name) if hit else "missing","point":[point.x,point.y,point.z]})
			if marked.contact:
				var tip=joint(record,"R Finger12")+person.global_basis*(vec(marked.tip)-vec(marked.marks["R Finger12"]))
				var token=scene.pieces[{"red":"Court14_RedHorse","black":"Court14_BlackHorse","greens":"Court14_SortingPod"}[role]]
				var gap=tip.distance_to(token.global_position+Vector3.UP*(.004 if role=="greens" else .013))
				max_touch=maxf(max_touch,gap);min_touch=minf(min_touch,gap);touch_frames+=1
			tested+=1
		hand_report[role]={"joint_max":worst_pose,"by_joint":stage,"touch_max":max_touch,"touch_min":min_touch,"contact_frames":touch_frames,"sampled":tested}
		contact_report[role]=fitted
		if worst_pose>.025 or max_touch>.012 or touch_frames<8:errors.append("motion_"+role)
		for f in fitted:
			if absf(f.error)>.024:errors.append("support_"+role+"_"+f.key)
	for sample in scene.layout.feet:
		var p=vec(sample)
		var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.11,p-Vector3.UP*.15,1))
		if hit:props_max=maxf(props_max,absf(hit.position.y-p.y))
		else:feet_misses.append(sample)
	if props_max>.025 or not feet_misses.is_empty():errors.append("wood_feet")
	var mounted=[]
	for anchor in scene.layout.mounts:
		var v=vec(anchor.at)
		var ray=space.intersect_ray(PhysicsRayQueryParameters3D.create(v+Vector3.LEFT*.14,v+Vector3.RIGHT*.12,1))
		mounted.append(str(ray.collider.get_parent().name) if ray else "missing")
		if not ray or str(ray.collider.get_parent().name)!=anchor.mesh:errors.append("kitchen_mount")
	var path:Curve3D=host.street_block.routes["west_doorstep"]
	var bad=[];var samples:=0;var probe=CapsuleShape3D.new();probe.radius=.23;probe.height=1.55
	for idx in range(ceili(path.get_baked_length()/.16)+1):
		var dist=minf(idx*.16,path.get_baked_length());var pos=path.sample_baked(dist)
		var tangent=(path.sample_baked(minf(dist+.15,path.get_baked_length()))-path.sample_baked(maxf(0.,dist-.15))).normalized()
		for off in [-.38,.0,.38]:
			var center=pos+tangent.cross(Vector3.UP).normalized()*off
			var floor_hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(center+Vector3.UP*.45,center-Vector3.UP*.60,1))
			if not floor_hit or floor_hit.normal.y<.65:bad.append([idx,off,"floor"]);continue
			var body=PhysicsShapeQueryParameters3D.new();body.shape=probe;body.collision_mask=1;body.transform.origin=floor_hit.position+Vector3.UP*.94
			for touch in space.intersect_shape(body,1):bad.append([idx,off,str(touch.collider.get_parent().name)])
			samples+=1
	if not bad.is_empty():errors.append("doorstep_path")
	var view:Dictionary=host.config.views.r24_west_life;var eye=vec(view.position);var dir=(vec(view.target)-eye).normalized()
	scene.set_physics_process(true)
	var maximum:=0;var stalls:=0;var greeting:=0.
	var before=[]
	var kitchen_clearance:Dictionary={}
	if host.art_profile.get("fitted_kitchen_r24",false):
		var envelope:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(study+"/kitchen/final_clearance.json"))
		var table:MeshInstance3D=scene.find_child("Court14_VegetableStand",true,false)
		var basins:MeshInstance3D=scene.find_child("Court14_EnamelBowls",true,false)
		var table_bounds:AABB=table.global_transform*table.get_aabb()
		var bowl_bounds:AABB=basins.global_transform*basins.get_aabb()
		var top:float=table_bounds.end.y
		var root_y:float=scene.residents.greens.person.global_position.y
		var gap:float=top-.03-(root_y+float(envelope.worst_knee_top))
		var brace_gap:float=top-.098-(root_y+float(envelope.worst_under_rail))
		var floor_gap:float=bowl_bounds.position.y-top
		kitchen_clearance={"table_height_local":top-root_y,"board_above_trousers":gap,"brace_above_trousers":brace_gap,"basin_base_to_table":floor_gap,"sampled_skin_frames":envelope.sampled.size()}
		if gap<.045 or brace_gap<.035 or absf(floor_gap)>.004:errors.append("kitchen_clearance")
	for t in host.street_block.tracks:before.append(t.node.position)
	for frame in 720:
		await physics_frame
		greeting=maxf(greeting,scene.eye_contact)
		if frame%15:continue
		var seen:=0
		for track in host.street_block.tracks:
			if track.car:continue
			var head=track.node.global_position+Vector3.UP*1.5;var ray=head-eye
			if ray.length()<35. and ray.normalized().dot(dir)>.70 and space.intersect_ray(PhysicsRayQueryParameters3D.create(eye,head,1)).is_empty():seen+=1
			if track.route=="west_doorstep" and track.d>path.get_baked_length()-.2 and track.wait>0:stalls+=1
		maximum=maxi(maximum,seen)
	var moved:=0;var total:=0
	for i in host.street_block.tracks.size():
		var track=host.street_block.tracks[i]
		if not track.car:
			total+=1
			if before[i].distance_to(track.node.position)>.2:moved+=1
	if maximum<2 or total!=21 or moved<20 or stalls<1 or greeting<.8:errors.append("street_life")
	var report={"passed":errors.is_empty(),"failures":errors,"art_revision":host.art_profile.art_revision,"poses":hand_report,"supports":contact_report,"kitchen_mounts":mounted,"furniture_contact_max":props_max,"furniture_contact_misses":feet_misses,"visit_samples":samples,"visit_blockers":bad,"west_visible_walkers_12s":maximum,"moving_walkers_12s":moved,"walkers":total,"stopped_at_door":stalls,"visitor_acknowledgment":greeting}
	preload("res://scripts/qa_context.gd").decorate(report,host)
	report["kitchen_clearance"]=kitchen_clearance
	DirAccess.make_dir_recursive_absolute(output)
	FileAccess.open(output+"/courtyard.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("COURT14_QA ",report.passed," ",errors," ",maximum," ",moved)
	quit(0 if errors.is_empty() else 3)

