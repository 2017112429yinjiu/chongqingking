extends Node3D

const BASE := "res://assets/frontage_r24/"
var manifest: Dictionary
var world: Node3D
var seller: Node3D
var motion: AnimationPlayer
var was_near := false
var cooldown := 0.0
var elapsed := 0.0
var greeting_count := 0
var result := {"donors":0,"missing":[],"stalls":2,"lights":0}

func install(city: Node3D) -> Dictionary:
	manifest=JSON.parse_string(FileAccess.get_file_as_string(BASE+"frontage.json"))
	var originals: Dictionary={}
	for node in city.find_children("*","MeshInstance3D",true,false):
		originals[str(node.name).replace(".","_")]=node
	for key in manifest.retire:
		var old: MeshInstance3D=originals.get(str(key).replace(".","_"))
		if old:old.hide()
		else:result.missing.append(key)
	var layer: Node3D=(load(BASE+"frontage.glb") as PackedScene).instantiate()
	add_child(layer)
	var fabric:=ShaderMaterial.new()
	fabric.shader=preload("res://shaders/frontage_canvas_r24.gdshader")
	fabric.set_shader_parameter("body",Color("#864e3e"))
	fabric.set_shader_parameter("stripe",Color("#ab9778"))
	var blue:=fabric.duplicate() as ShaderMaterial
	blue.set_shader_parameter("striped",false)
	blue.set_shader_parameter("body",Color("#546e72"))
	var timber:=ShaderMaterial.new()
	timber.shader=preload("res://shaders/frontage_surface_r24.gdshader")
	timber.set_shader_parameter("surface",load("res://assets/chongqing_district_wood_table_worn_diff_2k.jpg"))
	var steps:=timber.duplicate() as ShaderMaterial
	steps.set_shader_parameter("stone",true)
	steps.set_shader_parameter("surface",load("res://assets/street_r19/street_life_concrete_floor_worn_001_diff_2k.jpg"))
	var gravel:=steps.duplicate() as ShaderMaterial
	gravel.set_shader_parameter("surface",load("res://assets/chongqing_district_leaf_scattered_gravel_diff_2k.jpg"))
	var soil:=steps.duplicate() as ShaderMaterial
	soil.set_shader_parameter("surface",load("res://assets/chongqing_district_brown_mud_leaves_01_diff_2k.jpg"))
	var masonry:=steps.duplicate() as ShaderMaterial
	masonry.set_shader_parameter("retaining",true)
	masonry.set_shader_parameter("masonry_scan",load("res://assets/district_r21/terraces_mossy_stone_wall_diff_2k.jpg"))
	var asphalt:=steps.duplicate() as ShaderMaterial
	asphalt.set_shader_parameter("surface",load("res://assets/chongqing_district_asphalt_02_diff_1k.jpg"))
	var concrete:=steps.duplicate() as ShaderMaterial
	concrete.set_shader_parameter("viaduct",true)
	var enamel:=ShaderMaterial.new()
	enamel.shader=preload("res://shaders/stall_enamel_r24.gdshader")
	enamel.set_shader_parameter("tint",Color("#465a52"))
	for proxy in layer.find_children("*","MeshInstance3D",true,false):
		var label:=str(proxy.name)
		if manifest.donors.has(label):
			var donor: MeshInstance3D=originals.get(str(manifest.donors[label]).replace(".","_"))
			if donor==null:
				result.missing.append(manifest.donors[label])
				continue
			var finish:=donor.get_active_material(0)
			donor.mesh=proxy.mesh
			donor.global_transform=proxy.global_transform
			donor.set_surface_override_material(0,finish)
			proxy.get_parent().remove_child(proxy)
			proxy.free()
			result.donors+=1
		elif label.ends_with("_market_canvas"):proxy.set_surface_override_material(0,fabric)
		elif label.ends_with("_repair_canvas"):proxy.set_surface_override_material(0,blue)
		elif label.ends_with("_old_pine"):proxy.set_surface_override_material(0,timber)
		elif label.ends_with("_step_stone"):proxy.set_surface_override_material(0,steps)
		elif label.ends_with("_link_asphalt"):proxy.set_surface_override_material(0,asphalt)
		elif label.ends_with("_junction_stem"):proxy.set_surface_override_material(0,concrete)
		elif label.ends_with("_corner_stone"):proxy.set_surface_override_material(0,masonry)
		elif label.ends_with("_corner_cap") or label.ends_with("_corner_paving"):proxy.set_surface_override_material(0,steps)
		elif label.ends_with("_corner_grit"):proxy.set_surface_override_material(0,gravel)
		elif label.ends_with("_median_concrete"):proxy.set_surface_override_material(0,concrete)
		elif label.ends_with("_median_asphalt"):proxy.set_surface_override_material(0,asphalt)
		elif label.ends_with("_median_cinder"):proxy.set_surface_override_material(0,gravel)
		elif label.ends_with("_verge_soil"):proxy.set_surface_override_material(0,soil)
		elif label.ends_with("_verge_stone"):
			proxy.set_surface_override_material(0,gravel if label.begins_with("COL_R24_Verge_R24") else concrete)
		elif label.ends_with("_link_concrete"):
			proxy.set_surface_override_material(0,concrete)
			if label.begins_with("R24_FlyoverBox") or label.begins_with("R24_LinkCaps"):
				proxy.name="COL_"+label
		elif label.ends_with("_painted_iron"):proxy.set_surface_override_material(0,enamel)
	for item in manifest.fixtures:
		var body:=StaticBody3D.new()
		body.name="StallPost" if item.kind=="post" else "StallCounter"
		body.collision_layer=1
		body.collision_mask=0
		body.position=Vector3(item.position[0],item.position[1],item.position[2])
		var hitbox:=CollisionShape3D.new()
		if item.kind=="post":
			var post:=CylinderShape3D.new()
			post.radius=item.radius
			post.height=item.height
			hitbox.shape=post
		else:
			var counter:=BoxShape3D.new()
			counter.size=Vector3(item.size[0],item.size[1],item.size[2])
			hitbox.shape=counter
		body.add_child(hitbox)
		add_child(body,true)
	result.fixtures=manifest.fixtures.size()
	for p in manifest.lights:
		var light:=OmniLight3D.new()
		light.position=Vector3(p[0],p[1],p[2])
		light.light_color=Color("#ffdeaf")
		light.light_energy=.67
		light.omni_range=2.35
		light.distance_fade_enabled=true
		light.distance_fade_begin=14.
		light.distance_fade_length=8.
		add_child(light)
		result.lights+=1
	if not result.missing.is_empty():push_error("R24 donor missing: "+str(result.missing))
	return result

func start_life(main: Node3D) -> void:
	world=main
	for track in main.street_block.tracks:
		if track.car:add_contact_projection(track.node)
	for points in manifest.parked_contacts.values():install_parked_car(points)
	var seat: Array=manifest.resident
	seller=(load("res://assets/block_r23/neighbor.glb") as PackedScene).instantiate()
	seller.name="ProduceSeller"
	add_child(seller)
	seller.position=Vector3(seat[0],seat[1],seat[2])
	var feet:=PhysicsRayQueryParameters3D.create(seller.position+Vector3.UP*.40,seller.position-Vector3.UP*.55,1)
	var floor_hit:=get_world_3d().direct_space_state.intersect_ray(feet)
	if not floor_hit.is_empty() and floor_hit.normal.y>.65:
		seller.position.y=floor_hit.position.y+.006
	motion=seller.find_child("AnimationPlayer",true,false) as AnimationPlayer
	motion.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	motion.add_animation_library("stall",load(BASE+"stall_clips.res"))
	motion.play("stall/watch_street")
	motion.advance(.47)

func add_contact_projection(parent: Node3D) -> void:
	var shade:=Decal.new()
	shade.size=Vector3(2.5,.17,5.2)
	shade.position.y=.016
	shade.texture_albedo=preload("res://assets/frontage_r24/tyre_contact.png")
	shade.distance_fade_enabled=true
	shade.distance_fade_begin=34.
	shade.distance_fade_length=20.
	shade.normal_fade=.42
	shade.upper_fade=.16
	shade.lower_fade=.18
	parent.add_child(shade)

func install_parked_car(values: Array) -> void:
	var contacts: Array[Vector3]=[]
	var center:=Vector3.ZERO
	for row in values:
		var p:=Vector3(row[0],row[1],row[2])
		contacts.append(p)
		center+=p
	center/=4.
	var origin: Vector3=contacts.pop_front()
	contacts.sort_custom(func(a: Vector3,b: Vector3):return a.distance_squared_to(origin)<b.distance_squared_to(origin))
	var side:=contacts[0]-origin
	var lengthwise:=contacts[1]-origin
	var up:=lengthwise.cross(side).normalized()
	if up.y<0:up=-up
	var body:=StaticBody3D.new()
	body.name="ParkedCar"
	body.transform=Transform3D(Basis.looking_at(-lengthwise.normalized(),up),center)
	body.collision_layer=1
	body.collision_mask=0
	add_child(body,true)
	var shape:=BoxShape3D.new()
	shape.size=Vector3(side.length()+.14,1.14,lengthwise.length()+1.22)
	var collider:=CollisionShape3D.new()
	collider.shape=shape
	collider.position.y=.71
	body.add_child(collider)
	add_contact_projection(body)

func _physics_process(dt: float) -> void:
	if motion==null:return
	var delta: Vector3=world.explorer.camera.global_position-seller.global_position
	var distance:=delta.length()
	cooldown=maxf(0.,cooldown-dt)
	var at_counter: bool=world.explorer.walking and delta.z>.45 and delta.z<3.8 and absf(delta.x)<2.15 and absf(delta.y)<2.75
	if at_counter and not was_near and cooldown<=0.:
		motion.play("stall/greet",.36)
		greeting_count+=1
		cooldown=13.
	if motion.current_animation=="stall/greet" and (not at_counter or motion.current_animation_position>6.6):
		motion.play("stall/watch_street",.43)
	was_near=at_counter
	elapsed+=dt
	if distance>65.:
		seller.visible=false
		elapsed=0.
		return
	seller.visible=true
	var period:=.16 if distance>23. else (.07 if distance>11. else 0.)
	if elapsed>=period:
		motion.advance(elapsed)
		elapsed=0.


