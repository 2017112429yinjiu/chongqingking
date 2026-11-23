extends Node3D

const BASE := "res://assets/courtyard_r24/"
const WALKERS := "res://assets/block_r23/"
const PERIOD := 16.
var layout: Dictionary
var furnished_base := BASE
var residents: Dictionary = {}
var pieces: Dictionary = {}
var local_time := 0.
var main: Node3D
var report := {}
var elapsed := .5
var sorting_time := 2.
var visitor: Dictionary
var eye_contact := 0.
var listening := false

static func point(row: Array) -> Vector3:
	return Vector3(row[0],row[1],row[2])

static func install_paving(city: Node3D) -> Array:
	var library: Node3D = load(BASE+"paving.glb").instantiate()
	city.add_child(library)
	var replaced := []
	for kind in ["pavement","yard_concrete"]:
		var ground := city.find_child("COL_Terrain_200m_"+kind,true,false) as MeshInstance3D
		var donor := library.find_child("CourtPaving_"+kind,true,false) as MeshInstance3D
		if ground and donor:
			var surface := ground.get_active_material(0)
			ground.mesh=donor.mesh
			ground.global_transform=donor.global_transform
			ground.set_surface_override_material(0,surface)
			replaced.append(kind)
	library.free()
	return replaced

func install(city: Node3D, block: Node3D, fitted_kitchen: bool=false) -> Dictionary:
	furnished_base=BASE+"kitchen/" if fitted_kitchen else BASE
	layout=JSON.parse_string(FileAccess.get_file_as_string(furnished_base+"layout.json"))
	var old:Node=city.find_child("CourtRestingPlace",true,false)
	if old:old.free()
	for part in city.find_children("N13_ChessFurniture*","MeshInstance3D",true,false):
		part.free()
	var facade:=city.find_child("COL_B_A04_courtyard_home_plaster_grey",true,false) as MeshInstance3D
	if facade:
		var existing:=facade.get_active_material(0) as ShaderMaterial
		if existing:
			var plaster:=existing.duplicate() as ShaderMaterial
			plaster.set_shader_parameter("west_kitchen_weather",true)
			plaster.set_shader_parameter("west_kitchen_field",load(BASE+"west_plaster.png"))
			facade.material_override=plaster
	var objects:Node3D=load(furnished_base+"courtyard.glb").instantiate()
	add_child(objects)
	for record in layout.solids:
		var body:=StaticBody3D.new()
		add_child(body)
		body.position=point(record.at)
		body.rotation.y=record.yaw
		var collider:=CollisionShape3D.new()
		var shape:=BoxShape3D.new()
		shape.size=point(record.size)
		collider.shape=shape
		body.add_child(collider)
	for key in layout.motions:
		pieces[key]=objects.find_child(key,true,false)
	var visit:=Curve3D.new()
	visit.bake_interval=.22
	for sample in layout.visit:visit.add_point(point(sample))
	block.routes["west_doorstep"]=visit
	if FileAccess.file_exists(BASE+"return_corridors.json"):
		block.return_corridors=JSON.parse_string(FileAccess.get_file_as_string(BASE+"return_corridors.json"))
	report={"seats":layout.actors.size(),"chessmen":layout.pieces.size(),"visitor_length":visit.get_baked_length(),"missing":[]}
	return report

func start(host:Node3D) -> void:
	main=host
	for spec in layout.actors:
		var role:String=spec.role
		var model_name:="commuter" if role=="black" else "neighbor"
		var person:Node3D=load(WALKERS+model_name+".glb").instantiate()
		person.name="Courtyard_"+role
		add_child(person)
		person.position=point(spec.at)
		person.rotation.y=spec.yaw
		main.street_block.assign_outerwear(person,model_name,{"red":3,"black":1,"greens":2}[role])
		var animator:AnimationPlayer=person.find_children("*","AnimationPlayer",true,false)[0]
		var motion_folder:=furnished_base if role=="greens" else BASE
		var donor:Node=load(motion_folder+role+"_motion.glb").instantiate()
		var library_player:AnimationPlayer=donor.find_children("*","AnimationPlayer",true,false)[0]
		var library:=AnimationLibrary.new()
		var clip:Animation
		for label in library_player.get_animation_list():
			if label!="RESET":clip=library_player.get_animation(label);break
		assert(clip,"missing courtyard clip")
		# The imported animation has its own skeleton node path. The actor retains its original skin.
		var sk:Skeleton3D=person.find_children("*","Skeleton3D",true,false)[0]
		var actor_path:=animator.get_node(animator.root_node).get_path_to(sk)
		clip=clip.duplicate()
		for i in range(clip.get_track_count()):
			var path:=clip.track_get_path(i)
			if path.get_subname_count()>0:
				clip.track_set_path(i,NodePath(str(actor_path)+":"+str(path.get_concatenated_subnames())))
		clip.loop_mode=Animation.LOOP_LINEAR
		library.add_animation("activity",clip)
		animator.add_animation_library("courtyard",library)
		animator.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		animator.play("courtyard/activity")
		donor.free()
		var torso:=StaticBody3D.new()
		var hit:=CollisionShape3D.new()
		var capsule:=CapsuleShape3D.new()
		capsule.radius=.20;capsule.height=.86
		hit.shape=capsule;hit.position=Vector3(0,.79,.02)
		torso.add_child(hit);person.add_child(torso)
		residents[role]={"person":person,"player":animator,"bones":sk,"tier":0,"clock":-1.}
	for track in main.street_block.tracks:
		if track.route=="west_doorstep":visitor=track;break
	update_at(0.,true)

func _physics_process(delta:float) -> void:
	if not main:return
	local_time=fposmod(local_time+delta,PERIOD)
	var has_company:bool=not visitor.is_empty() and visitor.wait>.05 and visitor.node.position.distance_to(residents.greens.person.position)<2.1 and visitor.d>main.street_block.routes["west_doorstep"].get_baked_length()-.12
	var hands_clear:=fposmod(sorting_time-1.,4.)>2.40 and fposmod(sorting_time-1.,4.)<3.16
	listening=has_company and (listening or hands_clear)
	if not listening:sorting_time=fposmod(sorting_time+delta,PERIOD)
	eye_contact=move_toward(eye_contact,1. if listening else 0.,delta*2.2)
	update_at(local_time,false,delta)

func update_at(t:float,force_all:bool,delta:float=0.) -> void:
	elapsed+=delta
	var eye:Vector3=main.explorer.camera.global_position
	for role:String in residents:
		var rec:Dictionary=residents[role]
		var distance:=eye.distance_to(rec.person.global_position)
		var tier:=0 if distance<24. else (1 if distance<60. else 2)
		rec.tier=tier
		rec.person.visible=force_all or tier<2
		if not force_all and (tier==2 or (tier==1 and elapsed<.15)):continue
		var at:float=(fposmod(t+2.,PERIOD) if force_all else sorting_time) if role=="greens" else t
		rec.player.seek(at,true)
		rec.player.advance(0.)
		rec.clock=at
		if role=="greens" and not force_all and eye_contact>0.:look_at_visitor(rec)
	if elapsed>=.15:elapsed=0.
	for key:String in pieces:
		if not is_instance_valid(pieces[key]):continue
		var green:=key=="Court14_SortingPod"
		var first:=1.6 if key=="Court14_RedHorse" else 5.6
		var clock:float=(fposmod(t+2.,PERIOD) if force_all else sorting_time) if green else t
		if green:first=1.
		var interval:=4. if green else 8.
		var half_time:=fposmod(clock-first,2.*interval)
		var back:=half_time>=interval
		var progress:=smoothstep(.32,1.25,fmod(half_time,interval))
		var start:=point(layout.motions[key])
		var move:=point(layout.moves[key])
		var at:=start+move*((1.-progress) if back else progress)
		at.y+=.028*sin(progress*PI)
		pieces[key].global_position=at


func look_at_visitor(record:Dictionary) -> void:
	var skeleton:Skeleton3D=record.bones
	var bone:=skeleton.find_bone("Bip01 Head")
	if bone<0:bone=skeleton.find_bone("Bip01_Head")
	if bone<0:return
	var person:Node3D=record.person
	var forward:=person.global_basis.z.normalized()
	var direction:Vector3=visitor.node.position-person.position
	direction.y=0.
	var yaw:=clampf(forward.signed_angle_to(direction.normalized(),Vector3.UP),-.55,.55)
	var parent:=skeleton.get_bone_parent(bone)
	var basis:Basis=skeleton.global_basis*skeleton.get_bone_global_pose(parent).basis
	var parent_rotation:=basis.orthonormalized().get_rotation_quaternion()
	var turn:=Quaternion(Vector3.UP,yaw*eye_contact)*Quaternion(person.global_basis.x.normalized(),-.19*eye_contact)
	var pose:=skeleton.get_bone_pose_rotation(bone)
	skeleton.set_bone_pose_rotation(bone,parent_rotation.inverse()*turn*parent_rotation*pose)
