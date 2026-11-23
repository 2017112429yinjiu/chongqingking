extends SceneTree

const ROAD_WAYS := {"west":["1189963547","49182408"],"east":["1189963598","830761786"]}

func _initialize() -> void:
	call_deferred("survey")

func find_road(space: PhysicsDirectSpaceState3D, spot: Vector3, ways: Array) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(spot.x,32.,spot.z),Vector3(spot.x,-2.,spot.z),1)
	var skip: Array[RID]=[]
	for layer in 24:
		query.exclude=skip
		var hit:=space.intersect_ray(query)
		if hit.is_empty():break
		var label:=str(hit.collider.get_parent().name)
		for way in ways:
			if label.begins_with("COL_Road_"+way+"_") and label.ends_with("_asphalt"):
				return hit
		skip.append(hit.rid)
	return {}

func tyre_patches(hubs: Array) -> Array:
	var patches: Array=[]
	for hub in hubs:
		for instance in hub.find_children("*","MeshInstance3D",true,false):
			if not str(instance.name).to_lower().contains("tyre"):continue
			var mesh: MeshInstance3D=instance
			var points: PackedVector3Array=mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
			patches.append({"mesh":mesh,"verts":points})
	return patches

func sole(patch: Dictionary) -> Vector3:
	var t: Transform3D=patch.mesh.global_transform
	var contact:=Vector3.ZERO
	var minimum:=INF
	var count:=0
	for local: Vector3 in patch.verts:
		var p:=t*local
		if p.y<minimum-.0001:
			minimum=p.y
			contact=p
			count=1
		elif absf(p.y-minimum)<.0001:
			contact+=p
			count+=1
	return contact/float(count)

func survey() -> void:
	var world:=load("res://main.tscn").instantiate() as Node3D
	root.add_child(world)
	while world.street_block==null or world.street_block.tracks.size()!=8:await physics_frame
	var block: Node3D=world.street_block
	block.set_physics_process(false)
	var directory:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/traffic")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var out: Array=[]
	var passed:=true
	var checked:=0
	var space:=world.get_world_3d().direct_space_state
	for t in block.tracks:
		if not t.car:continue
		var curve: Curve3D=block.routes[t.route]
		var patches:=tyre_patches(t.hubs)
		var rows: Array=[]
		var miss:=0
		var peak:=0.
		var cover:=0
		var worst: Array=[]
		var gaps: Array[float]=[]
		var n:=ceili(curve.get_baked_length()/1.5)
		for i in range(n+1):
			t.d=curve.get_baked_length()*i/n
			block._pose(t,0.,true)
			for patch in patches:
				var p:=sole(patch)
				var hit:=find_road(space,p,ROAD_WAYS[t.route])
				if hit.is_empty():
					miss+=1
					rows.append([p.x,p.z,null])
					continue
				var gap: float=p.y-hit.position.y
				var near:=space.intersect_ray(PhysicsRayQueryParameters3D.create(hit.position+Vector3.UP*.60,hit.position-Vector3.UP*.09,1))
				var cover_height: float=0. if near.is_empty() else near.position.y-hit.position.y
				if cover_height>.10:cover+=1
				var row: Array=[p.x,p.z,gap,cover_height,str(near.get("collider").get_parent().name) if not near.is_empty() else ""]
				rows.append(row)
				gaps.append(absf(gap))
				if absf(gap)>peak:
					worst=row
					peak=absf(gap)
		gaps.sort()
		var ok:=patches.size()==4 and miss==0 and cover==0 and peak<.055 and gaps.size()==4*(n+1)
		checked+=rows.size()
		passed=passed and ok
		out.append({"route":t.route,"car":t.node.scene_file_path.get_file().get_basename(),"wheels":patches.size(),"missing":miss,"max_gap_m":peak,"p95_m":gaps[floori((gaps.size()-1)*.95)] if not gaps.is_empty() else -1.,"covered_over_10cm":cover,"worst":worst,"samples":rows})
	var parked: Array=[]
	var market=world.get_node_or_null("City/MarketTerraceR24")
	if market and market.manifest.has("parked_contacts"):
		for key in market.manifest.parked_contacts:
			for number in range(1,5):
				var wheel:=world.get_node("City").find_child("%s_%02d"%[key,number],true,false) as MeshInstance3D
				if not wheel:
					passed=false
					continue
				var p:=sole({"mesh":wheel,"verts":wheel.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]})
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.115,p-Vector3.UP*.46,1))
				var error: float=absf(p.y-hit.position.y) if not hit.is_empty() else 100.
				parked.append([wheel.name,error,str(hit.collider.get_parent().name) if not hit.is_empty() else ""])
				passed=passed and error<.043 and str(parked.back()[2]).begins_with("COL_Terrain")
		passed=passed and parked.size()==12
	var motion_report: Dictionary={}
	if "--traffic-motion" in OS.get_cmdline_user_args():
		block.set_physics_process(true)
		world.explorer.go_to_view("r24_junction")
		var cars: Array=[]
		for t in block.tracks:
			if t.car:
				t.d=block.routes[t.route].get_baked_length()*(.20 if cars.size()%2==0 else .58)
				block._pose(t,0.,true)
				cars.append({"track":t,"patches":tyre_patches(t.hubs),"last_x":-200.,"contacts":0,"miss":0,"max_error":0.})
		var ceiling:=INF
		var overhead_hits:=0
		for frame in 2520:
			await physics_frame
			if frame%9!=0:continue
			for record in cars:
				var t: Dictionary=record.track
				var pos: Vector3=t.node.global_position
				if pos.x<33. or pos.x>74. or absf(pos.x-record.last_x)<.1:continue
				record.last_x=pos.x
				for patch in record.patches:
					var p:=sole(patch)
					var h:=find_road(space,p,ROAD_WAYS[t.route])
					if h.is_empty():
						record.miss+=1
						continue
					record.contacts+=1
					record.max_error=maxf(record.max_error,absf(p.y-h.position.y))
				var ray:=PhysicsRayQueryParameters3D.create(pos+Vector3.UP*.18,pos+Vector3.UP*10.,1)
				var hit:=space.intersect_ray(ray)
				if not hit.is_empty() and str(hit.collider.get_parent().name).contains("FlyoverBox"):
					ceiling=minf(ceiling,hit.position.y-pos.y)
					overhead_hits+=1
		var live: Array=[]
		for record in cars:
			live.append([record.track.route,record.contacts,record.miss,record.max_error])
			passed=passed and record.contacts>=12 and record.miss==0 and record.max_error<.065
		motion_report={"physics_frames":2520,"cars":live,"soffit_hits":overhead_hits,"lowest_sampled_clearance_m":ceiling if overhead_hits else null}
		passed=passed and overhead_hits>0 and ceiling>3.0
	var report:={"passed":passed and out.size()==4,"checked":checked,"tracks":out,"live":motion_report,"parked_wheels":parked}
	preload("res://scripts/qa_context.gd").decorate(report,world)
	FileAccess.open(directory+"/traffic.json",FileAccess.WRITE).store_string(JSON.stringify(report))
	print("TRAFFIC_CONTACT ",report.passed," ",checked)
	quit(0 if report.passed else 2)
