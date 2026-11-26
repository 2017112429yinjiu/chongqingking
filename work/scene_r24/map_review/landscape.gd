extends "survey.gd"

func surface(x:float,n:float,guess:float) -> Vector3:
	var foot:=public_floor([x,n],guess)
	return foot if foot.is_finite() else Vector3(x,guess,-n)

func ground_hint(q:Vector2) -> float:
	var a:=Vector3(q.x,180,-q.y)
	var ray:=PhysicsRayQueryParameters3D.create(a,a-Vector3.UP*260,1)
	var omit:Array[RID]=[]
	var first:=0.
	for i in 45:
		ray.exclude=omit
		var hit:=scene.get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty():break
		if i==0:first=hit.position.y
		var n:=str(hit.collider.get_parent().name).to_lower()
		if "surface_" in n or "terrain" in n or "road" in n or "pavement" in n:return hit.position.y
		omit.append(hit.rid)
	return first

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	while not scene.gameplay:await physics_frame
	await frames(30)
	RenderingServer.render_loop_enabled=false
	scene.hud.hide()
	cam=Camera3D.new()
	scene.add_child(cam)
	cam.make_current()
	for x in range(-200,201,100):
		for n in range(-200,201,100):
			await picture("sector_%d_%d"%[x,n],"百米分区 · 鸟瞰",Vector3(x+9,132,-n+38),Vector3(x,12,-n),62.)
	var geo:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://source_data/geo_layout.json"))
	for category:String in ["buildings","context_buildings"]:
		for feature:Dictionary in geo[category]:
			var ring:=PackedVector2Array()
			for pt:Array in feature.points:ring.append(Vector2(pt[0],pt[1]))
			if ring[0].is_equal_approx(ring[-1]):ring.resize(ring.size()-1)
			var bounds:=Rect2(ring[0],Vector2.ZERO)
			for p:Vector2 in ring:bounds=bounds.expand(p)
			if not bounds.intersects(Rect2(-250,-250,500,500),true):continue
			var k:=0
			var longest:=0.
			for i in ring.size():
				var l:=ring[i].distance_to(ring[(i+1)%ring.size()])
				if l>longest:k=i;longest=l
			var a:=ring[k];var b:=ring[(k+1)%ring.size()]
			var mid:=(a+b)*.5;var axis:=a.direction_to(b)
			var normal:=Vector2(axis.y,-axis.x)
			if Geometry2D.is_point_in_polygon(mid+normal*.05,ring):normal=-normal
			var station:=mid+normal*clampf(longest*.6,8.,21.)
			var base:float=ground_hint(station) if feature.elevation==null else float(feature.elevation)
			var eye:=surface(station.x,station.y,base)+Vector3.UP*1.6
			await picture("outline_%s_%d"%[category,int(feature.id)],"地图轮廓外观",eye,Vector3(mid.x,base+clampf((float(feature.height) if feature.height!=null else 9.)*.36,2.3,12.),-mid.y))
	var probes:Dictionary={}
	for row:Dictionary in JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CQ_MAP_FLOORS"))):
		if not row.inner_above_15mm:continue
		var q:Array=row.inner_point
		var target:=enu(q)
		var space:=scene.get_world_3d().direct_space_state
		var near:=target+Vector3.UP*2.3
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(near,target-Vector3.UP*.22,1))
		probes[row.key]={"xy":q,"source_gap_m":row.inner_peak_m,"hit":str(scene.get_path_to(hit.collider)) if hit else "","rise_m":snappedf(hit.position.y-target.y,.001) if hit else null}
		# Look at the affected interior corner from its own building centre.
		var center:=target
		var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
		if str(row.key).begins_with("plot_"):
			for p:Dictionary in layout.plots:
				if int(p.plot_id)==int(str(row.key).get_slice("_",1)):center=world(p,0,0,0)
		else:
			for file:String in ["historic_courts","shancheng_lane"]:
				var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/"+file+".json"))
				for b:Dictionary in manifest.buildings:
					if b.get("id",b.get("osm",""))!=row.key:continue
					var ring:Array=b.get("ring",b.get("wall_base_corners",[]))
					var c:=Vector3.ZERO
					for a:Array in ring:c+=Vector3(a[0],target.y,-a[1])/ring.size()
					center=c
		var from:=target.move_toward(center,minf(3.4,target.distance_to(center)))+Vector3.UP*1.58
		await picture("floor_"+str(row.key).replace("@","_"),str(row.key),from,target+Vector3.UP*float(row.inner_peak_m))
	write_json("probes.json",probes)
	write_json("views.json",{"views":views})
	quit()
