extends RefCounted

static func _box(parent: Node, at: Vector3, size: Vector3) -> void:
	var body:=StaticBody3D.new()
	parent.add_child(body)
	body.position=at
	var collider:=CollisionShape3D.new()
	var shape:=BoxShape3D.new()
	shape.size=size
	collider.shape=shape
	body.add_child(collider)

static func run(main: Node3D) -> void:
	var tree:=main.get_tree()
	var runtime: Node3D=main.street_block
	var actor: Node3D=main.explorer
	var tests: Array=[]
	tests.append({"name":"all authored donor names resolve","pass":runtime.installation.missing.is_empty(),"details":runtime.installation})
	var before: Array=[]
	for track in runtime.tracks:
		before.append(track.node.position)
	for i in  range(180):await tree.physics_frame
	var moved: Array=[]
	var clips: Array=[]
	for i in runtime.tracks.size():
		var t: Dictionary=runtime.tracks[i]
		moved.append(t.node.position.distance_to(before[i]))
		if not t.car:clips.append(str(t.animation.current_animation) if t.animation else "")
	var neighborhood: bool=main.art_profile.get("neighborhood_r24",false)
	var expected_walkers:=21 if main.art_profile.get("courtyard_life_r24",false) else (19 if neighborhood else 4)
	var moving_count:=0
	for displacement in moved:
		if displacement>.50:moving_count+=1
	tests.append({"name":"vehicles and active walking clips advance on district routes","pass":moved.size()==4+expected_walkers and (moving_count>=expected_walkers+2 if neighborhood else moved.min()>1.1),"metres":moved})
	tests.append({"name":"walking clips imported and active","pass":clips.size()==expected_walkers and not clips.has(""),"clips":clips})
	actor.set_mode(true)
	for i in range(3):await tree.physics_frame
	tests.append({"name":"walking body attached and visible","pass":is_instance_valid(actor.body_view) and actor.body_view.is_visible_in_tree()})
	actor._looking=true
	var look:=InputEventMouseMotion.new()
	look.relative=Vector2(32.,48.)
	var old_yaw: float=actor.camera.rotation.y
	actor._unhandled_input(look)
	tests.append({"name":"mouse motion turns captured walking camera without right-button event","pass":absf(old_yaw-actor.camera.rotation.y)>.03})
	var world: PhysicsDirectSpaceState3D=main.get_world_3d().direct_space_state
	var capsule:=CapsuleShape3D.new()
	capsule.height=1.62;capsule.radius=.22
	var obstructions: Array=[]
	var count:=0
	for name in ["walk","promenade"]:
		var curve: Curve3D=runtime.routes[name]
		for distance_m in range(1,floori(curve.get_baked_length()),2):
			var centre:=curve.sample_baked(distance_m)
			var ray:=PhysicsRayQueryParameters3D.create(centre+Vector3.UP*.48,centre-Vector3.UP*.65,1)
			var road:=world.intersect_ray(ray)
			if road.is_empty():
				obstructions.append([name,distance_m,"unsupported"])
				continue
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=capsule;query.collision_mask=1
			query.transform.origin=road.position+Vector3.UP*.93
			for item in world.intersect_shape(query,1):
				obstructions.append([name,distance_m,str(item.collider.get_parent().name)])
			count+=1
	tests.append({"name":"pedestrian route capsule clearance every two metres","pass":obstructions.is_empty(),"samples":count,"obstructions":obstructions})
	var heights: Array=[]
	for z in [31.7,32.83,33.9]:
		for x in [-27.85,-27.3]:
			var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,20,z),Vector3(x,11,z),1))
			heights.append(hit.position.y if hit else 999.)
	tests.append({"name":"A05 shutter exterior collision clears sill at six points","pass":heights.max()<13.865,"heights":heights})
	var vehicle: Node3D=main.gameplay.scooter
	var fixture:=Node3D.new()
	main.add_child(fixture)
	_box(fixture,Vector3(71,59.9,81),Vector3(6,.2,18))
	_box(fixture,Vector3(71,60.04,80),Vector3(6,.08,4))
	_box(fixture,Vector3(71,60.60,76),Vector3(6,1.2,.30))
	vehicle.global_position=Vector3(71,60.04,85.5)
	vehicle.rotation=Vector3.ZERO
	vehicle.automation=true
	vehicle.enter(actor)
	vehicle.test_throttle=1.
	var crest:=0.
	for i in range(370):
		await tree.physics_frame
		if vehicle.position.z<81.3 and vehicle.position.z>78.7:crest=maxf(crest,vehicle.position.y)
	tests.append({"name":"mounted scooter rolls across 80 mm seam and stops before solid wall","pass":crest>60.059 and vehicle.position.z>76.1 and vehicle.position.z<77.5,"crest_m":crest,"stopped_at":str(vehicle.position),"speed":vehicle.speed})
	var report:={"engine":Engine.get_version_info().string,"tests":tests,"passed":true}
	for t in tests:
		if not t["pass"]:report.passed=false
	preload("res://scripts/qa_context.gd").decorate(report,main)
	var dest:=preload("res://scripts/qa_context.gd").directory("res://verification_r23/current")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dest))
	var f:=FileAccess.open(dest+"/block_test.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  "));f.close()
	print("R23_TEST ",JSON.stringify(report))
	tree.quit(0 if report.passed else 1)

