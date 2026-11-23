extends Node3D

const BASE := "res://assets/block_r23/"
var routes: Dictionary = {}
var tracks: Array[Dictionary] = []
var manifest: Dictionary
var installation := {"swapped":0, "hidden":0, "missing":[], "routes":{}, "actors":0}
var main: Node3D
var clock_s := 0.0

func _v(data: Array) -> Vector3:
	return Vector3(data[0], data[1], data[2])

func install(city: Node3D, lane_data: Dictionary={}) -> Dictionary:
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
			fabric.shader=preload("res://shaders/cotton_r23.gdshader")
			var src := proxy.get_active_material(0) as BaseMaterial3D
			if src:fabric.set_shader_parameter("dye",src.albedo_color)
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
	var specifications := [
		["west","taxi",.24,6.5],["west","microvan",.64,5.9],["east","microvan",.37,6.2],["east","taxi",.81,7.1],
		["walk","neighbor",.27,1.13],["walk","commuter",.77,.64],
		["promenade","neighbor",.52,1.05],["promenade","commuter",.29,.71]]
	for spec in specifications:
		var curve: Curve3D = routes[spec[0]]
		var node := (load(BASE+spec[1]+".glb") as PackedScene).instantiate() as Node3D
		add_child(node)
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
		track["errand_phase"]=0
		tracks.append(track)
		_pose(track,0.,true)
	installation.actors=tracks.size()

func _pose(t: Dictionary, advance: float, snap: bool) -> void:
	var curve: Curve3D = routes[t.route]
	var node: Node3D = t.node
	var a := curve.sample_baked(maxf(0.,t.d-.36))
	var b := curve.sample_baked(minf(curve.get_baked_length(),t.d+.36))
	var direction: Vector3 = (b-a)*float(t.sign)
	node.position=curve.sample_baked(t.d)
	if direction.length_squared()<.00001:return
	if not t.car:
		direction.y=0
		var right:=direction.normalized().cross(Vector3.UP)
		node.position+=right*.31
		if is_inside_tree():
			var ray:=PhysicsRayQueryParameters3D.create(node.position+Vector3.UP*.46,node.position-Vector3.UP*.63,1)
			var floor_hit:=get_world_3d().direct_space_state.intersect_ray(ray)
			if not floor_hit.is_empty() and floor_hit.normal.y>.63:
				node.position.y=floor_hit.position.y+.007
	var target := Basis.looking_at(direction.normalized(),Vector3.UP,not t.car)
	node.basis=target if snap else node.basis.slerp(target,1.-exp(-advance*7.)).orthonormalized()
	if t.car:
		for wheel in t.hubs:wheel.rotate_x(-float(t.v)*advance/.29)
	elif t.animation:
		t.animation.speed_scale = 1.
		t.animation.advance(advance*float(t.v)/float(t.pace))

func _physics_process(delta: float) -> void:
	if not is_instance_valid(main) or not is_instance_valid(main.explorer):return
	clock_s+=delta
	var actor: Node3D=main.explorer.camera
	for t in tracks:
		var node: Node3D=t.node
		var range_m:=actor.global_position.distance_to(node.position)
		t.debt+=delta
		var tick:=0. if range_m<31 else (.10 if range_m<68 else .35)
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
				t.sign=-float(t.sign);t.wait=1.8;t.v=0.;t.errand_phase=0
		_pose(t,dt,false)

