extends Node3D

const RUN_SECONDS = 5.0
var remaining := 0.0
var stream_mesh := MeshInstance3D.new()
var splash := CPUParticles3D.new()
var sound := AudioStreamPlayer3D.new()

func setup(outlet: Vector3, ground_y: float) -> void:
	global_position = outlet
	var length_m := outlet.y - ground_y
	var jet := CylinderMesh.new()
	jet.top_radius = .007
	jet.bottom_radius = .004
	jet.height = length_m
	jet.radial_segments = 9
	jet.rings = 24
	var water := StandardMaterial3D.new()
	water.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water.albedo_color = Color(.61,.72,.73,.48)
	water.roughness = .09
	var flow_material := ShaderMaterial.new()
	flow_material.shader=preload("res://shaders/rinse_water.gdshader")
	jet.material=flow_material
	stream_mesh.mesh = jet
	stream_mesh.position.y = -length_m*.5
	stream_mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	stream_mesh.hide()
	add_child(stream_mesh)
	var drop := SphereMesh.new()
	drop.radius = .0028
	drop.height = .007
	drop.radial_segments = 5
	drop.rings = 2
	drop.material = water
	splash.mesh = drop
	splash.amount = 24
	splash.lifetime = .22
	splash.direction = Vector3.UP
	splash.spread = 65.
	splash.initial_velocity_min = .24
	splash.initial_velocity_max = .70
	splash.gravity = Vector3.DOWN * 7.5
	splash.position.y = -length_m+.012
	splash.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	splash.emitting = false
	add_child(splash)
	var loop := preload("res://assets/lane_r20/rinse.wav").duplicate() as AudioStreamWAV
	loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
	loop.loop_end = roundi(loop.get_length()*loop.mix_rate)
	sound.stream = loop
	sound.unit_size = 1.0
	sound.volume_db = -7.
	sound.max_distance = 8.
	add_child(sound)
	set_physics_process(false)

func toggle() -> void:
	if remaining > 0.:
		close()
		return
	remaining = RUN_SECONDS
	stream_mesh.show()
	splash.emitting = true
	sound.play()
	set_physics_process(true)

func close() -> void:
	remaining = 0.
	stream_mesh.hide()
	splash.emitting = false
	sound.stop()
	set_physics_process(false)

func _physics_process(delta: float) -> void:
	remaining -= delta
	if remaining <= 0.:
		close()
