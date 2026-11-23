extends RefCounted
## The A04 leaf is decorative wood. Its collision backing is recessed into the wall.
const FACE_NAME := "R17_Entry_A04_0_timber"
const NORMAL := Vector3.RIGHT
const BEATS := [.76,1.18,1.60]
var point := Vector3.ZERO
var stream := AudioStreamWAV.new()

func locate(city: Node3D) -> bool:
	var leaf := city.find_child(FACE_NAME,true,false) as MeshInstance3D
	if not leaf: return false
	var center := leaf.to_global(leaf.get_aabb().get_center())
	var aim := center+Vector3(0,.345,.21)
	var start := leaf.to_local(aim+NORMAL)
	var end := leaf.to_local(aim-NORMAL)
	var faces := leaf.mesh.get_faces()
	var nearest := INF
	for i in range(0,faces.size(),3):
		var hit = Geometry3D.segment_intersects_triangle(start,end,faces[i],faces[i+1],faces[i+2])
		if hit==null: continue
		var distance:=start.distance_squared_to(hit)
		if distance<nearest:
			nearest=distance
			point=leaf.to_global(hit)
	if nearest==INF:return false
	stream.format=AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate=22050
	var bytes:=PackedByteArray()
	bytes.resize(2*3087)
	var noise:=RandomNumberGenerator.new()
	noise.seed=71033
	for i in 3087:
		var t:=float(i)/22050.
		var thud:=sin(TAU*156*t)*exp(-43*t)+.53*sin(TAU*321*t)*exp(-65*t)
		var attack:=noise.randf_range(-.33,.33)*exp(-270*t)
		bytes.encode_s16(2*i,roundi(9300*(thud+attack)*minf(i/12.,1.)))
	stream.data=bytes
	return true

func sound(parent: Node3D,beat:int) -> void:
	var source:=AudioStreamPlayer3D.new()
	source.stream=stream
	source.max_distance=10.
	source.pitch_scale=[.97,1.05,1.][beat%3]
	parent.add_child(source)
	source.global_position=point
	source.finished.connect(source.queue_free)
	source.play()

func clearance(t:float) -> float:
	var nearest:=1.
	for beat:float in BEATS:
		var before:=beat-t
		var fraction:=clampf(before/.145 if before>=0. else -before/.16,0.,1.)
		nearest=minf(nearest,smoothstep(.0,1.,fraction))
	return .115*nearest
