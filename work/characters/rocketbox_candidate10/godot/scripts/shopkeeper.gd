extends Node3D
var animator: AnimationPlayer
var available_clips: Dictionary = {}
var skeleton: Skeleton3D
var food: Node3D
var food_start: Vector3
var food_end: Vector3
var packing: bool=false
var held: bool=false
var released: bool=false
var last_greeting: float=-30.0
var visitor_present: bool=false
var visitor_absent_since: float=-1.0
var attention: SkeletonModifier3D
var eyelids: Array[Dictionary]=[]
var smiles: Array[Dictionary]=[]
var blink_clock: float=0.0
var blink_count: int=0
var next_blink: float=3.8
var autonomous: bool=true
const SERVE_SECONDS: float=3.2
const GRASP_TIME: float=1.12
const RELEASE_TIME: float=2.40
const HANDLE_HEIGHT: float=.331

func _ready() -> void:
	# Run after AnimationPlayer so the held bag uses this frame's hand pose.
	process_priority=10
	var model: Node3D = load("res://assets/characters/shopkeeper_r18.glb").instantiate()
	add_child(model)
	for node: Node in model.find_children("*","AnimationPlayer",true,false):
		animator = node
		break
	skeleton = model.find_children("*","Skeleton3D",true,false)[0]
	attention=preload("res://scripts/shopkeeper_attention.gd").new()
	attention.host=self
	skeleton.add_child(attention)
	for mesh: MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
		var smile_index: int=mesh.find_blend_shape_by_name("Smile")
		if smile_index>=0:smiles.append({"mesh":mesh,"index":smile_index})
		if str(mesh.name).contains("eyebrow") or str(mesh.name).contains("eyelashes"):
			mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		for name: String in ["Blink_left","Blink_right"]:
			var index: int=mesh.find_blend_shape_by_name(name)
			if index>=0:eyelids.append({"mesh":mesh,"index":index})
		for surface in range(mesh.mesh.get_surface_count()):
			var source: Material=mesh.mesh.surface_get_material(surface)
			if source is StandardMaterial3D:
				var mat: StandardMaterial3D=source.duplicate()
				if mat.resource_name.contains("body"):
					mat.albedo_color=Color(.92,.97,1,1)
					mat.subsurf_scatter_enabled=true
					mat.subsurf_scatter_skin_mode=true
					mat.subsurf_scatter_strength=.10
					mat.roughness=.60
				if mat.resource_name.contains("low-poly"):
					mat.roughness=.14
					mat.metallic_specular=.5
					mat.clearcoat_enabled=true
					mat.clearcoat=.30
					mat.clearcoat_roughness=.08
				if mat.resource_name.contains("eyebrow"):
					mat.albedo_color=Color(1.35,1.32,1.28,1)
					mat.roughness=.65
					# Preserve fractional strand coverage; hard clipping made painted blocks.
					mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
					mat.alpha_antialiasing_mode=BaseMaterial3D.ALPHA_ANTIALIASING_OFF
				if mat.transparency==BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR:
					mat.alpha_antialiasing_mode=BaseMaterial3D.ALPHA_ANTIALIASING_ALPHA_TO_COVERAGE
				mesh.set_surface_override_material(surface,mat)
	if animator:
		for clip: String in animator.get_animation_list():
			if clip.to_lower().contains("idle"):
				available_clips["idle"] = clip
				animator.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
			elif clip.to_lower().contains("serve"):
				available_clips["serve"] = clip
			elif clip.to_lower().contains("greet"):
				available_clips["greet"] = clip
		animator.animation_finished.connect(func(_clip): packing=false; play_state("idle"))
		play_state("idle")
	var body: StaticBody3D = StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var shape: CapsuleShape3D = CapsuleShape3D.new()
	shape.radius = .27
	shape.height = 1.65
	var collider: CollisionShape3D = CollisionShape3D.new()
	collider.shape = shape
	collider.position.y = .825
	body.add_child(collider)
	add_child(body)

func play_state(state: String) -> void:
	if animator and available_clips.has(state):
		if state=="serve":
			attention.tracking=false
			packing=true
			held=false
			released=false
			if food:
				food.global_position=food_start
				food.visible=true
		animator.play(available_clips[state],.25)

func grip_position() -> Vector3:
	skeleton.force_update_all_bone_transforms()
	var hand: Transform3D=skeleton.global_transform*skeleton.get_bone_global_pose(skeleton.find_bone("hand_r"))
	# The handle belongs inside the curled fingers, distal to the mid-palm.
	# Authored against the exported finger joint positions and a close engine view.
	return hand*Vector3(-.024,.095,.012)

func configure_food(bag: Node3D) -> void:
	food=bag
	animator.play(available_clips["serve"],0)
	animator.seek(GRASP_TIME,true)
	animator.advance(0)
	food_start=grip_position()-Vector3.UP*HANDLE_HEIGHT
	animator.seek(RELEASE_TIME,true)
	animator.advance(0)
	food_end=grip_position()-Vector3.UP*HANDLE_HEIGHT
	food.global_position=food_start
	animator.play(available_clips["idle"],0)
	animator.advance(0)

func update_food_contact() -> void:
	if not food or not packing: return
	var t: float=animator.current_animation_position
	if t<GRASP_TIME:
		food.global_position=food_start
	elif t<RELEASE_TIME:
		held=true
		food.global_position=grip_position()-Vector3.UP*HANDLE_HEIGHT
	else:
		released=true
		food.global_position=food_end

func greet_nearby(observer: Vector3) -> void:
	var ground_distance: float=Vector2(observer.x,observer.z).distance_to(Vector2(global_position.x,global_position.z))
	var local_observer: Vector3=to_local(observer)
	var in_front: bool=local_observer.z>.15 and absf(atan2(local_observer.x,local_observer.z))<1.10
	attention.tracking=autonomous and not packing and ground_distance<4.5 and in_front
	attention.target=observer
	if packing or not autonomous: return
	var now: float=Time.get_ticks_msec()/1000.0
	# Recognize an arrival once; don't nod on a timer at a stationary customer.
	if ground_distance>4.5 or not in_front:
		if visitor_absent_since<0:visitor_absent_since=now
		if now-visitor_absent_since>2.0:visitor_present=false
		return
	visitor_absent_since=-1.0
	if ground_distance<3.0 and not visitor_present and now-last_greeting>8:
		visitor_present=true
		last_greeting=now
		play_state("greet")

func set_blink(value: float) -> void:
	for entry in eyelids:entry.mesh.set_blend_shape_value(entry.index,value)

func set_smile(value: float) -> void:
	for entry in smiles:entry.mesh.set_blend_shape_value(entry.index,value)

func _process(delta: float) -> void:
	update_food_contact()
	if packing and autonomous and food:
		# Watch the handle being reached for, lifted and set down.
		attention.target=food.global_position+Vector3.UP*HANDLE_HEIGHT
		attention.tracking=true
	if not autonomous:return
	var smile: float=.04
	if animator.current_animation==available_clips.get("greet",""):
		smile+=.30*sin(PI*minf(1,animator.current_animation_position/2.5))
	set_smile(smile)
	blink_clock+=delta
	var phase: float=blink_clock-next_blink
	set_blink(sin(PI*phase/.18)*.96 if phase>0 and phase<.18 else 0.0)
	if phase>=.18:
		blink_count+=1
		next_blink=blink_clock+[4.7,3.6,5.4,4.2][blink_count%4]
