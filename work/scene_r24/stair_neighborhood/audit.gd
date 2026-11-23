extends SceneTree
func _initialize()->void: call_deferred("run_checks")

func v(a: Array)->Vector3:return Vector3(a[0],a[1],a[2])

func run_checks()->void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null or main.street_block.tracks.is_empty(): await physics_frame
	for tick in 3:await physics_frame
	var data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/neighborhood_r24/layout.json"))
	var space=main.get_world_3d().direct_space_state
	var checks={}
	var rail_errors=[]
	for name_of_mesh in data.retire:
		var node=main.get_node("City").find_child(name_of_mesh,true,false)
		if node!=null and (node.is_visible_in_tree() or node.find_child("GeneratedWorldBody",true,false)!=null):rail_errors.append(name_of_mesh)
	checks["retired_remaining"]=rail_errors
	var trees=[]
	for tree in JSON.parse_string(FileAccess.get_file_as_string("res://assets/neighborhood_r24/trunk_sections.json")):
		var center=v(tree.base)+Vector3.UP*.60
		var circle=space.intersect_ray(PhysicsRayQueryParameters3D.create(center+Vector3.RIGHT*(tree.radius+.12),center,1))
		trees.append(circle and str(circle.collider.name)=="NeighborhoodTreeTrunks")
	checks["trunk_collisions"]=trees
	var tested_mounts=[]
	for wire in data.wires:
		for mount in wire.mounts:
			var p=v(mount.foot);var normal=v(mount.normal)
			var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+normal*.17,p-normal*.15,1))
			tested_mounts.append({"span":wire.name,"source":mount.mesh,"error":hit.position.distance_to(p) if hit else 99.,"hit":str(hit.collider.get_parent().name) if hit else ""})
	checks["mounts"]=tested_mounts
	var wall_hits=0;var near_court=0
	var wall_fails=[];var other_solids=[]
	for probe in data.wall_probes:
		var p=v(probe.p);var along=v(probe.edge[1])-v(probe.edge[0])
		var across=Vector3(along.z,0.,-along.x).normalized()
		var ok=false
		for sign_value in [-1.,1.]:
			var q=PhysicsRayQueryParameters3D.create(p+across*.095*sign_value,p-across*.095*sign_value,1)
			var hidden_by:Array[RID]=[]
			for layer_idx in 8:
				q.exclude=hidden_by
				var hit=space.intersect_ray(q)
				if hit.is_empty():break
				var mesh_name=str(hit.collider.get_parent().name)
				if mesh_name=="COL_N13_BankCutFaces":
					ok=true
					break
				other_solids.append([probe.p,mesh_name])
				hidden_by.append(hit.rid)
			if ok:break
		if ok:
			wall_hits+=1
			if p.x< -19 and p.x> -22. and p.z>10. and p.z<18.:near_court+=1
		else:
			var detail=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+across*.095,p-across*.095,1))
			wall_fails.append([probe.p,str(detail.collider.get_parent().name) if detail else "nothing"])
	checks["sealed_edges"]={"tested":data.wall_probes.size(),"hits":wall_hits,"at_reported_corner":near_court,"misses":wall_fails,"covering_geometry":other_solids}
	var props=[]
	var groups:Array=data.adjustments.duplicate()
	for checked in data.ground_audit:
		if checked.status=="already_seated":groups.append(checked)
	for group in groups:
		var worst=0.;var miss=0;var unexpected=[]
		for point in group.contacts:
			var p=v(point)
			var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.17,p-Vector3.UP*.23,1))
			if not hit:miss+=1
			else:
				var dist=absf(hit.position.y-p.y);worst=maxf(worst,dist)
				if dist>.06:unexpected.append([point,str(hit.collider.name),str(hit.collider.get_parent().name),hit.position.y-p.y])
		props.append({"group":group.group,"points":group.contacts.size(),"max_m":worst,"miss":miss,"unexpected":unexpected})
	checks["prop_contacts"]=props
	var capsule=CapsuleShape3D.new()
	capsule.height=1.54;capsule.radius=.22
	var route_results={}
	for key in ["walk","promenade","central_stairs","west_stairs","market_apron"]:
		var path:Curve3D=main.street_block.routes[key]
		var misses=[];var count=0
		for sample_idx in range(1,int(path.get_baked_length()/.42)):
			var at:float=sample_idx*.42
			var base=path.sample_baked(at)
			var dir=(path.sample_baked(at+.15)-path.sample_baked(at-.15)).normalized()
			var right=Vector3(dir.z,0,-dir.x).normalized()
			for side in [-.38,.38]:
				var p=base+right*side
				if main.street_block.walking_lanes.has(key):p=main.street_block.walk_position(key,at,signf(side))
				var ground=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.50,p-Vector3.UP*.75,1))
				if not ground or ground.normal.y<.58:
					misses.append([at,side,"no floor"]);continue
				var query=PhysicsShapeQueryParameters3D.new()
				query.shape=capsule;query.transform.origin=ground.position+Vector3.UP*.94;query.collision_mask=1
				for hit in space.intersect_shape(query,1):misses.append([at,side,str(hit.collider.get_parent().name)])
				count+=1
		route_results[key]={"samples":count,"fail":misses}
	checks["footways"]=route_results
	var start=[];var distances=[]
	for t in main.street_block.tracks:start.append(t.node.global_position);distances.append(0.)
	var max_seen={}
	for frame in range(360):
		await physics_frame
		if frame%10!=0:continue
		for i in main.street_block.tracks.size():
			var t=main.street_block.tracks[i];distances[i]+=t.node.global_position.distance_to(start[i]);start[i]=t.node.global_position
		for name_of_view in ["r23_main_road","r24_west_life","r24_center_seam","r24_lane_life"]:
			var view:Dictionary=main.config.views[name_of_view];var eye=v(view.position);var axis=(v(view.target)-eye).normalized();var within=0
			for t in main.street_block.tracks:
				if t.car:continue
				var head=t.node.global_position+Vector3.UP*1.50;var rel=head-eye
				if rel.length()>35 or rel.normalized().dot(axis)<.70:continue
				if space.intersect_ray(PhysicsRayQueryParameters3D.create(eye,head,1)).is_empty():within+=1
			max_seen[name_of_view]=maxi(int(max_seen.get(name_of_view,0)),within)
	var foot=0;var advanced=0
	for i in main.street_block.tracks.size():
		if not main.street_block.tracks[i].car:
			foot+=1
			if distances[i]>.5:advanced+=1
	checks["pedestrians"]={"total":foot,"moving_6s":advanced,"visible_in_35m":max_seen}
	var expected_people=21 if main.art_profile.get("courtyard_life_r24",false) else 19
	var valid=main.scene_identity.get("neighborhood",{}).get("missing",["install"]).is_empty() and rail_errors.is_empty() and near_court>=8 and wall_fails.is_empty() and foot==expected_people and advanced==foot
	valid=valid and trees.size()==5 and not trees.has(false)
	for row in tested_mounts:valid=valid and row.error<.025 and row.hit==row.source
	for row in props:valid=valid and row.miss==0 and row.max_m<.06
	for key in route_results:valid=valid and route_results[key].fail.is_empty()
	for key in max_seen:valid=valid and max_seen[key]>=1
	if main.art_profile.get("canopy_distance_r24",false):
		checks["tree_distance_meshes"]=main.scene_identity.neighborhood.get("tree_distance_meshes",0)
		valid=valid and checks.tree_distance_meshes==288
	checks["passed"]=valid
	preload("res://scripts/qa_context.gd").decorate(checks,main)
	var dir=preload("res://scripts/qa_context.gd").directory()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	FileAccess.open(dir+"/neighborhood.json",FileAccess.WRITE).store_string(JSON.stringify(checks,"  "))
	print("CQ_BLOCK_LIFE ",valid," ",foot," ",advanced," ",wall_hits," ",near_court)
	quit(0 if valid else 3)

