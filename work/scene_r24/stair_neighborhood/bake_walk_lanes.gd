extends SceneTree
var sample_shape:=CapsuleShape3D.new()
var space:PhysicsDirectSpaceState3D
func _initialize()->void:call_deferred("bake")

func support(p:Vector3)->Variant:
	var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.45,p-Vector3.UP*.76,1)
	var hit:=space.intersect_ray(query)
	if hit.is_empty() or hit.normal.y<.62:return null
	var mesh_name:=str(hit.collider.get_parent().name)
	if mesh_name=="City" or mesh_name=="Neighborhood13" or mesh_name.begins_with("COL_N13_Planting") or mesh_name.begins_with("COL_N13_Lamp"):return null
	var height:float=hit.position.y
	var capsule:=PhysicsShapeQueryParameters3D.new()
	capsule.collision_mask=1;capsule.shape=sample_shape;capsule.transform.origin=Vector3(p.x,height+.94,p.z)
	var contacts:=space.intersect_shape(capsule,4)
	if not contacts.is_empty():
		if not mesh_name.begins_with("COL_Walk_") or not mesh_name.contains("step_concrete"):return null
		for contact in contacts:
			if str(contact.collider.get_parent().name) not in [mesh_name,"COL_R23_PathFoundations"]:return null
		var next_height=height
		for angle_idx in 12:
			var a=TAU*angle_idx/12.
			var sample_at=p+Vector3(cos(a),0,sin(a))*.235
			var ray=PhysicsRayQueryParameters3D.create(Vector3(sample_at.x,height+.28,sample_at.z),Vector3(sample_at.x,height-.30,sample_at.z),1)
			var tread=space.intersect_ray(ray)
			if tread.is_empty() or str(tread.collider.get_parent().name)!=mesh_name or tread.normal.y<.8:return null
			next_height=maxf(next_height,tread.position.y)
		if next_height<=height+.005 or next_height-height>.20:return null
		capsule.transform.origin.y=next_height+.94
		if not space.intersect_shape(capsule,1).is_empty():return null
	return Vector3(p.x,height+.007,p.z)

func explain(at: Vector3)->Array:
	var h=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.45,at-Vector3.UP*.76,1))
	if h.is_empty():return ["no floor"]
	var q=PhysicsShapeQueryParameters3D.new()
	q.shape=sample_shape;q.collision_mask=1;q.transform.origin=h.position+Vector3.UP*.94
	var bodies=[]
	for hit in space.intersect_shape(q,4):bodies.append(str(hit.collider.get_parent().name))
	var rim=[]
	for k in 8:
		var pt=h.position+Vector3(cos(k*TAU/8),0,sin(k*TAU/8))*.235
		var tread=space.intersect_ray(PhysicsRayQueryParameters3D.create(pt+Vector3.UP*.35,pt-Vector3.UP*.35,1))
		rim.append([str(tread.collider.get_parent().name),snappedf(tread.position.y-h.position.y,.001)] if tread else [])
	return [str(h.collider.get_parent().name),bodies,rim]

func bake()->void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while main.gameplay==null or main.street_block.tracks.is_empty():await physics_frame
	for i in 4:await physics_frame
	space=main.get_world_3d().direct_space_state
	sample_shape.height=1.62;sample_shape.radius=.235
	var lanes={};var errors=[];var tight=[]
	for key in ["walk","promenade","market_apron","west_stairs","central_stairs"]:
		var route:Curve3D=main.street_block.routes[key];var length:=route.get_baked_length()
		var intervals=ceili(length/.28)
		var data={"length":length}
		for dir in [1.,-1.]:
			var samples=[];var last_offset:float=.37*dir
			for idx in range(intervals+1):
				var station:float=length*idx/intervals;var pos=route.sample_baked(station)
				var tangent=(route.sample_baked(minf(length,station+.18))-route.sample_baked(maxf(0.,station-.18))).normalized()
				var side=tangent.cross(Vector3.UP).normalized()
				var options=[.37,.30,.46,.23,.55,.15,.65,.08,.76,0.,.88,-.12,1.,-.25,-.39,-.55,1.17,-.72,-.92]
				options.sort_custom(func(a,b):return absf(a-.37)+.62*absf(a*dir-last_offset)<absf(b-.37)+.62*absf(b*dir-last_offset))
				var picked:Variant=null
				for offset in options:
					var at=pos+side*offset*dir
					var hit=support(at)
					if hit==null:continue
					# Checks on both sides of the sample protect the interpolated section at a corner.
					if support(at+tangent*.12)==null or support(at-tangent*.12)==null:continue
					if not samples.is_empty():
						var last:Array=samples.back()
						var prev=Vector3(last[0],last[1],last[2])
						if support(prev.lerp(hit,.5))==null or absf(prev.y-hit.y)>.33:continue
					picked=hit;last_offset=offset*dir
					if offset<.18:tight.append([key,dir,station,offset])
					break
				if picked==null:
					errors.append([key,dir,station,[pos.x,pos.y,pos.z],explain(pos+side*.37*dir),explain(pos+side*.37*dir+tangent*.12),explain(pos+side*.37*dir-tangent*.12)])
					picked=pos
				samples.append([picked.x,picked.y,picked.z])
			data["forward" if dir>0 else "backward"]=samples
		lanes[key]=data
	var dest=OS.get_cmdline_user_args()[-1]
	FileAccess.open(dest+"/lane_bake_report.json",FileAccess.WRITE).store_string(JSON.stringify({"unresolved":errors,"constrained":tight},"  "))
	if errors.is_empty():
		FileAccess.open("res://assets/neighborhood_r24/walk_lanes.json",FileAccess.WRITE).store_string(JSON.stringify(lanes))
	print("BAKE_NEIGHBORHOOD ",errors.size()," ",tight.size())
	quit(0 if errors.is_empty() else 2)

