extends Node3D

const BASE := "res://assets/block_r23/"
var routes: Dictionary = {}
var tracks: Array[Dictionary] = []
var manifest: Dictionary
var installation := {"swapped":0, "hidden":0, "missing":[], "routes":{}, "actors":0}
var return_corridors:Dictionary={}
var outfit_materials := {}
var walking_lanes := {}
var street_passing: RefCounted
var main: Node3D
var clock_s := 0.0

func _v(data: Array) -> Vector3:
	return Vector3(data[0], data[1], data[2])

func install(city: Node3D, lane_data: Dictionary={}, washcloth: Shader=null) -> Dictionary:
	manifest = JSON.parse_string(FileAccess.get_file_as_string(BASE+"block.json"))
	var layer := (load(BASE+"block.glb") as PackedScene).instantiate() as Node3D
	var city_meshes := {}
	for o in city.find_children("*","MeshInstance3D",true,false):
		city_meshes[str(o.name).replace(".","_")] = o
	# Tie colour, relief and roughness to a single metric course datum across each masonry shell.
	var brick_count := 0
	for key in city_meshes:
		if not str(key).begins_with("COL_B_") or not (str(key).ends_with("_brick") or str(key).ends_with("_brick_dark")):continue
		var face: MeshInstance3D=city_meshes[key]
		var old: Material=face.get_active_material(0)
		if not old is ShaderMaterial or old.shader!=preload("res://shaders/street_surface_r19.gdshader"):continue
		var skin:=old.duplicate() as ShaderMaterial
		var dark: bool=str(key).ends_with("_brick_dark")
		var library: String="res://assets/chongqing_district_brick_wall_"+("08_" if dark else "09_")
		var resolution: String="2k" if dark else "1k"
		skin.set_shader_parameter("albedo_map",load(library+"diff_"+resolution+".jpg"))
		skin.set_shader_parameter("normal_map",load(library+"nor_gl_"+resolution+".jpg"))
		skin.set_shader_parameter("rough_map",load(library+"rough_"+resolution+".png"))
		skin.set_shader_parameter("rough_channel",Vector4(1,0,0,0))
		skin.set_shader_parameter("street_brick",true)
		skin.set_shader_parameter("masonry_repeat_m",Vector2(2.38,1.39) if dark else Vector2(3.94,2.15))
		face.set_surface_override_material(0,skin)
		brick_count+=1
	installation["brick_shells"]=brick_count
	add_child(layer)
	for proxy in layer.find_children("*","MeshInstance3D",true,false):
		var label := str(proxy.name)
		if manifest.donors.has(label):
			var source: String = manifest.donors[label]
			var donor := city_meshes.get(source.replace(".","_")) as MeshInstance3D
			if not donor:
				installation.missing.append(source)
				continue
			var mat := donor.get_active_material(0)
			donor.mesh = proxy.mesh
			donor.global_transform = proxy.global_transform
			donor.set_surface_override_material(0,mat)
			proxy.get_parent().remove_child(proxy)
			proxy.free()
			installation.swapped += 1
		elif label.begins_with("R23_Towel_"):
			var fabric := ShaderMaterial.new()
			fabric.shader=washcloth if washcloth else preload("res://shaders/cotton_r23.gdshader")
			var src := proxy.get_active_material(0) as BaseMaterial3D
			if src:fabric.set_shader_parameter("dye",src.albedo_color)
			if washcloth:
				var cloth_bounds: Vector3 = proxy.get_aabb().size
				fabric.set_shader_parameter("cloth_size_m",Vector2(Vector2(cloth_bounds.x,cloth_bounds.z).length(),cloth_bounds.y))
				fabric.set_shader_parameter("loop_pile",preload("res://assets/frontage_r24/terry_pile.png"))
				fabric.set_shader_parameter("phase",str(label).get_slice("_",2).to_int() * 1.37)
			else:
				fabric.set_shader_parameter("phase",label.to_int()*.79)
			proxy.set_surface_override_material(0,fabric)
		elif label == "R23_Street_R23_oiled_bamboo" or label == "R23_Room_R23_oiled_bamboo":
			var timber:=ShaderMaterial.new()
			timber.shader=preload("res://shaders/furniture_wood_r23.gdshader")
			proxy.set_surface_override_material(0,timber)
		elif label == "COL_R23_NanquSidewalk":
			var paving := ShaderMaterial.new()
			paving.shader=preload("res://shaders/sidewalk_r23.gdshader")
			paving.set_shader_parameter("surface",load("res://assets/street_r19/street_life_concrete_floor_worn_001_diff_2k.jpg"))
			paving.set_shader_parameter("relief",load("res://assets/street_r19/street_life_concrete_floor_worn_001_nor_gl_2k.jpg"))
			proxy.set_surface_override_material(0,paving)
		elif label in ["COL_R23_PathFoundations","COL_R23_NanquRetaining","COL_R23_NanquUpperApron"]:
			var facade := city_meshes.get("COL_Court_retaining_stone") as MeshInstance3D
			if facade:
				var stone := ShaderMaterial.new()
				stone.shader=preload("res://shaders/foundation_r23.gdshader")
				var stone_source: Material = facade.get_active_material(0)
				if stone_source is BaseMaterial3D and stone_source.albedo_texture:
					stone.set_shader_parameter("aggregate",stone_source.albedo_texture)
				elif stone_source is ShaderMaterial and stone_source.get_shader_parameter("albedo_map"):
					stone.set_shader_parameter("aggregate",stone_source.get_shader_parameter("albedo_map"))
				proxy.set_surface_override_material(0,stone)
	for raw in manifest.hide:
		var target := city_meshes.get(str(raw).replace(".","_")) as MeshInstance3D
		if target:target.hide();installation.hidden += 1
		else:installation.missing.append(raw)
	for coords in manifest.lights:
		var practical := OmniLight3D.new()
		practical.position=Vector3(coords[0],coords[2]-.16,-coords[1])
		practical.light_color=Color(.99,.82,.61)
		practical.light_energy=.52
		practical.omni_range=2.7
		practical.distance_fade_enabled=true
		practical.distance_fade_begin=16
		practical.distance_fade_length=12
		add_child(practical)
	var authored: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"routes.json"))
	for key in lane_data:
		authored[key]=lane_data[key].points
	for key in authored:
		var path := Curve3D.new()
		path.bake_interval=.32
		for xyz in authored[key]:path.add_point(_v(xyz))
		routes[key]=path
		installation.routes[key]=path.get_baked_length()
	if not installation.missing.is_empty():push_error("R23 missing city mesh %s"%str(installation.missing))
	return installation

func start_simulation(world: Node3D) -> void:
	main=world
	if world.art_profile.get("market_passing_r24",false):
		street_passing=preload("res://scripts/pedestrian_passing_r24.gd").new()
	var specifications := [
		["west","taxi",.24,6.5],["west","microvan",.64,5.9],["east","microvan",.37,6.2],["east","taxi",.81,7.1],
		["walk","neighbor",.27,1.13],["walk","commuter",.77,.64],
		["promenade","neighbor",.52,1.05],["promenade","commuter",.29,.71]]
	if world.art_profile.get("neighborhood_r24",false):
		specifications.append_array([
			["promenade","commuter",.11,.94],["promenade","neighbor",.38,.91],["promenade","commuter",.63,1.09],["promenade","neighbor",.83,.88],
			["walk","commuter",.16,1.00],["walk","neighbor",.48,.93],["walk","commuter",.89,.96],
			["market_apron","neighbor",.21,.79],["market_apron","commuter",.67,.94],["market_apron","neighbor",.88,.83],
			["central_stairs","neighbor",.24,.77],["central_stairs","commuter",.68,.70],["central_stairs","neighbor",.89,.79],
			["west_stairs","commuter",.35,.71],["west_stairs","neighbor",.77,.83]])
	if world.art_profile.get("courtyard_life_r24",false):
		specifications.append_array([["west_stairs","neighbor",.51,.88],["west_doorstep","commuter",.69,.85]])
	for spec in specifications:
		var curve: Curve3D = routes[spec[0]]
		var node := (load(BASE+spec[1]+".glb") as PackedScene).instantiate() as Node3D
		add_child(node)
		if tracks.size()>=8:
			assign_outerwear(node,spec[1],tracks.size()%5)
		var is_car: bool = spec[0] in ["west","east"]
		var player := node.find_child("AnimationPlayer",true,false) as AnimationPlayer
		if player:
			player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
			for anim in player.get_animation_list():
				if anim=="RESET":continue
				player.get_animation(anim).loop_mode=Animation.LOOP_LINEAR
				player.play(anim)
				player.seek(float(spec[2])*player.get_animation(anim).length,true)
				break
		var track := {"node":node,"route":spec[0],"d":curve.get_baked_length()*float(spec[2]),
			"pace":spec[3],"v":spec[3],"sign":1. if is_car or spec[1]=="neighbor" else -1.,
			"wait":0.,"debt":0.,"car":is_car,"animation":player,"hubs":node.find_children("Hub*","Node3D",true,false)}
		if spec[0]=="west_doorstep":track.sign=1.
		if world.art_profile.get("natural_stops_r24",false) and not is_car:
			player.add_animation_library("street_wait",load("res://assets/courtyard_r24/wait_clips.res"))
			track["standing"]="street_wait/"+str(spec[1])
			track["walk_clip"]=str(player.current_animation)
			track["stopped"]=false
			track["turn_from"]=0.
			track["turn_station"]=0.
		track["errand_phase"]=0
		track["district_pedestrian"] = not is_car and world.art_profile.get("neighborhood_r24",false)
		track["lane_offset"] = (.32+.09*fmod(float(spec[2])*7.,1.)) if track.district_pedestrian else .31
		if spec[0]=="west_doorstep":track.lane_offset=0.
		if street_passing and not is_car:street_passing.install(track)
		tracks.append(track)
		_pose(track,0.,true)
	installation.actors=tracks.size()

func assign_outerwear(person: Node3D, model_name: String, choice: int) -> void:
	if choice==0:return
	var key := "%s_%d" % [model_name,choice]
	var hues := [Vector3.ONE,Vector3(.50,.75,.97),Vector3(.60,.71,.48),Vector3(.90,.65,.52),Vector3(.53,.75,.73)]
	for body: MeshInstance3D in person.find_children("*","MeshInstance3D",true,false):
		for face in body.mesh.get_surface_count():
			var source := body.get_active_material(face) as BaseMaterial3D
			if not source or not source.resource_name.ends_with("_body"):continue
			if not outfit_materials.has(key):
				var cloth := ShaderMaterial.new()
				cloth.shader=preload("res://shaders/pedestrian_outerwear_r24.gdshader")
				cloth.set_shader_parameter("original",source.albedo_texture)
				cloth.set_shader_parameter("red_jacket",model_name=="commuter")
				cloth.set_shader_parameter("dyed_cloth",hues[choice])
				outfit_materials[key]=cloth
			body.set_surface_override_material(face,outfit_materials[key])

func walk_position(route: String, station: float, direction: float) -> Vector3:
	var lane: Dictionary=walking_lanes[route]
	var samples: Array=lane.forward if direction>0. else lane.backward
	var at:=clampf(station/float(lane.length)*(samples.size()-1),0.,samples.size()-1.)
	var i:=mini(floori(at),samples.size()-2)
	return _v(samples[i]).lerp(_v(samples[i+1]),at-i)

func turn_position(t:Dictionary,station:float) -> Vector3:
	var destination:=walk_position(t.route,station,t.sign)
	if not t.has("turn_from") or t.turn_from==0.:return destination
	var dist:=absf(station-float(t.turn_station))
	var turn:Dictionary=return_corridors[t.route]["start" if t.turn_station<.01 else "end"]
	var blend:=smoothstep(float(turn.begin),float(turn.end),dist)
	return walk_position(t.route,station,t.turn_from).lerp(destination,blend)

func _pose(t: Dictionary, advance: float, snap: bool) -> void:
	var curve: Curve3D = routes[t.route]
	var node: Node3D = t.node
	var a := curve.sample_baked(maxf(0.,t.d-.36))
	var b := curve.sample_baked(minf(curve.get_baked_length(),t.d+.36))
	var direction: Vector3 = (b-a)*float(t.sign)
	node.position=curve.sample_baked(t.d)
	var measured_lane: bool=not t.car and walking_lanes.has(t.route)
	if measured_lane:
		node.position=turn_position(t,t.d)
		direction=(turn_position(t,t.d+.32)-turn_position(t,t.d-.32))*float(t.sign)
	if direction.length_squared()<.00001:return
	if not t.car:
		direction.y=0
		var right:=direction.normalized().cross(Vector3.UP)
		if not measured_lane:node.position+=right*float(t.lane_offset)
		if t.has("passing_offset"):
			node.position+=street_passing.lateral_step(t,node.position,direction.normalized(),curve.get_baked_length(),advance,main.explorer,tracks)
			if absf(t.passing_speed)>.03:
				direction=(direction.normalized()*maxf(.34,t.v)+right*float(t.passing_speed)).normalized()
		if is_inside_tree() and (not t.district_pedestrian or snap or node.global_position.distance_squared_to(main.explorer.camera.global_position)<3600.):
			var ray:=PhysicsRayQueryParameters3D.create(node.position+Vector3.UP*.46,node.position-Vector3.UP*.63,1)
			var floor_hit:=get_world_3d().direct_space_state.intersect_ray(ray)
			if not floor_hit.is_empty() and floor_hit.normal.y>.63:
				node.position.y=floor_hit.position.y+.007
	if t.route=="west_doorstep" and t.wait>0. and t.d>curve.get_baked_length()-.1:
		direction=Vector3(-67.12,node.position.y,18.49)-node.position
	var target := Basis.looking_at(direction.normalized(),Vector3.UP,not t.car)
	var turn_amount:=1.-exp(-advance*7.)
	if t.has("standing") and t.wait>0.:
		var remaining:=node.basis.orthonormalized().get_rotation_quaternion().angle_to(target.get_rotation_quaternion())
		turn_amount=minf(turn_amount,deg_to_rad(136.)*advance/maxf(.001,remaining))
	node.basis=target if snap else node.basis.slerp(target,turn_amount).orthonormalized()
	if t.car:
		for wheel in t.hubs:wheel.rotate_x(-float(t.v)*advance/.29)
	elif t.animation and (not t.district_pedestrian or node.visible):
		t.animation.speed_scale = 1.
		if t.has("standing"):
			var motion_speed:=Vector2(float(t.v),float(t.get("passing_speed",0.))).length()
			var stop_now:bool=motion_speed<(.28 if t.stopped else .17)
			if stop_now!=t.stopped:
				t.stopped=stop_now
				t.animation.play(t.standing if stop_now else t.walk_clip,.32)
			t.animation.advance(advance if stop_now else advance*clampf(motion_speed/float(t.pace),.45,1.35))
		else:t.animation.advance(advance*float(t.v)/float(t.pace))

func _physics_process(delta: float) -> void:
	if not is_instance_valid(main) or not is_instance_valid(main.explorer):return
	clock_s+=delta
	var actor: Node3D=main.explorer.camera
	for t in tracks:
		var node: Node3D=t.node
		var range_m:=actor.global_position.distance_to(node.position)
		t.debt+=delta
		var tick:=0. if range_m<31 else (.10 if range_m<68 else .35)
		if t.district_pedestrian:
			node.visible=range_m<108.
			tick=0. if range_m<23 else (.10 if range_m<52 else .38)
		if t.debt<tick:continue
		var dt: float=t.debt
		t.debt=0.
		var curve: Curve3D=routes[t.route]
		var limit:=curve.get_baked_length()
		var wanted: float=t.pace
		if t.wait>0.:
			t.wait=maxf(0.,float(t.wait)-dt)
			wanted=0.
		if not t.car:
			var observer: Vector3=main.explorer.body.global_position-node.position
			if main.explorer.walking and absf(observer.y)<1.7 and node.basis.z.dot(observer)>.05 and observer.length()<.98:wanted=0.
			if t.district_pedestrian:
				for person in tracks:
					if person.route==t.route and person.sign!=t.sign and t.sign<0 and walking_lanes.has(t.route):
						var approaching:float=(person.d-t.d)*t.sign
						if approaching>0. and approaching<1.55:
							var middle:float=(person.d+t.d)*.5
							if walk_position(t.route,middle,1).distance_to(walk_position(t.route,middle,-1))<.52:wanted=0.
					if person.route==t.route and person.sign==t.sign:
						var gap: float=(person.d-t.d)*t.sign
						if gap>.001 and gap<1.15:wanted=minf(wanted,maxf(0.,(gap-.61)*1.7))
			# Each out-and-back errand includes a short stop at its frontage, once per leg.
			var marker: float=limit*(.43 if t.sign>0 else .66)
			if t.errand_phase==0 and absf(float(t.d)-marker)<.38:
				t.wait=2.1 if t.pace>1. else 3.7
				t.errand_phase=1
		if t.car:
			var forward: Vector3=-node.basis.z
			if main.explorer.walking:
				var obstacle: Vector3=main.explorer.body.global_position-node.global_position
				var ahead:=forward.dot(obstacle)
				if absf(obstacle.y)<2. and ahead>-.9 and ahead<4.+t.v*.75 and (obstacle-forward*ahead).length()<1.8:wanted=0.
			var scooter_delta: Vector3=main.gameplay.scooter.global_position-node.global_position
			var scooter_ahead:=forward.dot(scooter_delta)
			if absf(scooter_delta.y)<1.7 and scooter_ahead>-.75 and scooter_ahead<4.+t.v*.7 and (scooter_delta-forward*scooter_ahead).length()<1.45:wanted=0.
			for other in tracks:
				if other.route==t.route and other.d>t.d and other.d-t.d<5.3+t.v*.65:wanted=0.
		t.v=move_toward(t.v,wanted,dt*(3.5 if t.car else 1.5))
		t.d=clampf(float(t.d)+float(t.sign)*float(t.v)*dt,0.,limit)
		if (t.sign>0. and t.d>=limit) or (t.sign<0. and t.d<=0.):
			if t.car:
				if range_m>32 and actor.global_position.distance_to(curve.sample_baked(0.))>32:
					t.d=0.;_pose(t,0.,true)
				else:t.v=0.
			else:
				if t.has("turn_from") and return_corridors.has(t.route):
					t.turn_from=t.sign;t.turn_station=t.d
				t.sign=-float(t.sign);t.wait=5.4 if t.route=="west_doorstep" and t.d>=limit else 1.8;t.v=0.;t.errand_phase=0
		_pose(t,dt,false)

