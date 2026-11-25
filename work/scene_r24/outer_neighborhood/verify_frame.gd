extends "../../scene_r24/outer_neighborhood/survey.gd"

const FRAME_LAYER := 1 << 14
var samples := {}
var misses := []
var worst_error := 0.0

func cast(a: Vector3, b: Vector3, mask: int) -> Dictionary:
	var ray := PhysicsRayQueryParameters3D.create(a, b, mask)
	ray.hit_back_faces = true
	return scene.get_world_3d().direct_space_state.intersect_ray(ray)

func face_at(plot: Dictionary, kind: String, target: Vector3, outward: Vector3) -> void:
	var hit := cast(target + outward*.075, target - outward*.075, FRAME_LAYER)
	samples[kind] = int(samples.get(kind, 0)) + 1
	var error := INF if hit.is_empty() else target.distance_to(hit.position)
	if error > .007:
		misses.append({"plot": plot.plot_id, "kind": kind, "target": str(target), "hit": str(hit.get("position", ""))})
	else:
		worst_error = maxf(worst_error, error)

func court_point(p: Dictionary, x: float, v: float, h: float) -> Vector3:
	return world(p,p.court.center_u + p.court.stair_side*x, p.depth/2.0+v, h)

func gallery(p: Dictionary) -> void:
	var obj=scene.find_child("COL_Outer500_Court_%02d"%int(p.plot_id),true,false)
	if not obj or not obj.get_node_or_null("CQ_StaticCollision"):
		misses.append({"plot":p.plot_id,"kind":"missing gallery body"})
		return
	var body: StaticBody3D=obj.get_node("CQ_StaticCollision")
	body.collision_layer |= FRAME_LAYER
	var w: float=p.court.half_width
	var h: float=p.court.upper_m
	var end: float=p.court.landing_v-p.depth/2.0-.84
	var left: float=-w+.28
	var right: float=w-.22
	var xs: Array[float]=[left+.24,(left+.30)*.5,.30,(.30+right)*.5,right-.24]
	var forward: Vector3=(court_point(p,0,1,0)-court_point(p,0,0,0)).normalized()
	for x in xs:
		face_at(p,"gallery_shoe",court_point(p,x,end+.085,.21),-forward)
		face_at(p,"gallery_lower_post",court_point(p,x,end+.11,h-.51),-forward)
		face_at(p,"gallery_upper_post",court_point(p,x,end+.12,h+.35),-forward)
	for j in xs.size()-1:
		face_at(p,"gallery_girder",court_point(p,(xs[j]+xs[j+1])*.5,end+.20,h-.40),Vector3.DOWN)
	for bounds: Array in [[left,.30],[.30,right]]:
		for j in range(1,ceili((bounds[1]-bounds[0])/.77)):
			face_at(p,"bedroom_joist",court_point(p,bounds[0]+j*.77,10.85,h+2.17),Vector3.DOWN)
	body.collision_layer &= ~FRAME_LAYER

func verify() -> void:
	output=OS.get_environment("CQ_QA_DIR")
	scene=load("res://first_shift.tscn").instantiate()
	root.add_child(scene)
	for tick in 1600:
		if scene.get("gameplay"): break
		await physics_frame
	await frames(12)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var columns := 0
	var storeys := 0
	var max_span := 0.0
	for p: Dictionary in data.plots:
		var f: Dictionary = p.frame
		var obj = scene.find_child("COL_Outer500_Frame_%02d" % int(p.plot_id), true, false)
		if not obj or not obj.get_node_or_null("CQ_StaticCollision"):
			misses.append({"plot": p.plot_id, "kind": "missing frame body"})
			continue
		var body: StaticBody3D = obj.get_node("CQ_StaticCollision")
		body.collision_layer |= FRAME_LAYER
		var u_axis := (world(p,1,0,0)-world(p,0,0,0)).normalized()
		var portal: float = p.door_u
		var foundation := cast(world(p,portal,p.depth*.25,.22),world(p,portal,p.depth*.25,-.26),1)
		samples["ground_floor"] = int(samples.get("ground_floor",0)) + 1
		if foundation.is_empty() or absf(foundation.position.y-p.height-.035)>.018:
			misses.append({"plot":p.plot_id,"kind":"ground floor","hit":str(foundation.get("position",""))})
		columns += f.u.size()*f.v.size()
		storeys += int(p.floors)
		for level in range(int(p.floors)):
			var base: float = level * f.storey
			var soffit: float = base + f.storey - f.slab
			for i in f.u.size():
				var u: float = f.u[i]
				for j in f.v.size():
					var v: float = f.v[j]
					# At the right exterior wall, approach the exposed inside face.
					var side := -1.0 if i==f.u.size()-1 else 1.0
					face_at(p,"column",world(p,u+side*f.radius,v,base+1.26),side*u_axis)
					if level==0:
						face_at(p,"post_base",world(p,u,v,-.18),Vector3.DOWN)
					if i+1 < f.u.size():
						var end_u: float = f.u[i+1]
						max_span=maxf(max_span,end_u-u)
						for where: float in [u+f.radius+.04,(u+end_u)/2,end_u-f.radius-.04]:
							face_at(p,"cross_beam",world(p,where,v,soffit-f.transverse_drop),Vector3.DOWN)
					if j+1 < f.v.size():
						var end_v: float = f.v[j+1]
						max_span=maxf(max_span,end_v-v)
						for where: float in [v+f.radius+.04,(v+end_v)/2,end_v-f.radius-.04]:
							face_at(p,"long_beam",world(p,u,where,soffit-f.longitudinal_drop),Vector3.DOWN)
					if i+1 < f.u.size() and j+1 < f.v.size():
						var mid_u: float = (u+f.u[i+1])*.5
						var mid_v: float = (v+f.v[j+1])*.5
						face_at(p,"slab_bottom",world(p,mid_u,mid_v,soffit),Vector3.DOWN)
						face_at(p,"slab_top",world(p,mid_u,mid_v,soffit+f.slab),Vector3.UP)
						var blocked:=cast(world(p,mid_u,mid_v,base+.08),world(p,mid_u,mid_v,soffit-.08),FRAME_LAYER)
						samples["clear_bay"] = int(samples.get("clear_bay",0)) + 1
						if not blocked.is_empty(): misses.append({"plot":p.plot_id,"kind":"filled bay","floor":level})
		body.collision_layer &= ~FRAME_LAYER
		if p.has("court"): gallery(p)
	var report={"engine":Engine.get_version_info().string,"plots":data.plots.size(),"columns":columns,
		"storeys":storeys,"max_bay_axis_m":max_span,"max_surface_error_m":worst_error,"samples":samples,"failures":misses}
	FileAccess.open(output.path_join("frame_contacts.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	quit(0 if misses.is_empty() and storeys>0 else 2)
