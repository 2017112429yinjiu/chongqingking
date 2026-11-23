extends Node3D
## Original reusable folded-paper takeaway prop; geometry in metres.
var ticket: Label3D
func _ready() -> void:
	var paper: StandardMaterial3D=StandardMaterial3D.new()
	paper.albedo_color=Color(.56,.39,.22)
	paper.roughness=.94
	paper.cull_mode=BaseMaterial3D.CULL_DISABLED
	var cross: Array[Vector2]=[Vector2(-1,-1),Vector2(1,-1),Vector2(1,0),Vector2(1,1),Vector2(-1,1),Vector2(-1,0)]
	var levels: Array[Vector3]=[Vector3(.108,.003,.068),Vector3(.123,.055,.079),Vector3(.116,.22,.074),Vector3(.119,.255,.076)]
	var rings: Array=[]
	for level in levels:
		var ring: Array[Vector3]=[]
		for i in range(cross.size()):
			var inset: float=.85 if i==2 or i==5 else 1.0
			ring.append(Vector3(cross[i].x*level.x*inset,level.y,cross[i].y*level.z))
		rings.append(ring)
	var builder: SurfaceTool=SurfaceTool.new()
	builder.begin(Mesh.PRIMITIVE_TRIANGLES)
	for r in range(rings.size()-1):
		for i in range(cross.size()):
			var j: int=(i+1)%cross.size()
			for vertex: Vector3 in [rings[r][i],rings[r+1][i],rings[r+1][j],rings[r][i],rings[r+1][j],rings[r][j]]:
				builder.add_vertex(vertex)
	builder.generate_normals()
	var body: MeshInstance3D=MeshInstance3D.new()
	body.mesh=builder.commit()
	var bag_stock:=ShaderMaterial.new()
	bag_stock.shader=preload("res://scripts/kraft_paper.gdshader")
	body.material_override=bag_stock
	add_child(body)
	# Closed base and actual packed food: the open bag must not be an empty shell.
	var base: MeshInstance3D=MeshInstance3D.new()
	var bottom: BoxMesh=BoxMesh.new()
	bottom.size=Vector3(.214,.003,.132)
	base.mesh=bottom
	base.position.y=.003
	base.material_override=paper
	add_child(base)
	var kraft: StandardMaterial3D=StandardMaterial3D.new()
	kraft.albedo_color=Color(.66,.50,.30)
	kraft.roughness=.88
	var lid: StandardMaterial3D=StandardMaterial3D.new()
	lid.albedo_color=Color(.78,.80,.76)
	lid.roughness=.28
	lid.metallic_specular=.45
	_lathe("PackedNoodleBowl",[Vector2(.048,.010),Vector2(.052,.018),Vector2(.064,.141),Vector2(.066,.146),Vector2(.064,.150)],kraft,true)
	_lathe("ClosedFoodLid",[Vector2(0,.153),Vector2(.047,.153),Vector2(.057,.155),Vector2(.062,.153),Vector2(.067,.150),Vector2(.067,.144)],lid)
	var sleeve: MeshInstance3D=MeshInstance3D.new()
	var wrapped_chopsticks: BoxMesh=BoxMesh.new()
	wrapped_chopsticks.size=Vector3(.012,.228,.007)
	sleeve.mesh=wrapped_chopsticks
	sleeve.material_override=kraft
	sleeve.position=Vector3(.082,.122,.025)
	sleeve.rotation.z=-.07
	add_child(sleeve)
	for side in [-1.0,1.0]:
		var handle: MeshInstance3D=MeshInstance3D.new()
		var strip: SurfaceTool=SurfaceTool.new()
		strip.begin(Mesh.PRIMITIVE_TRIANGLES)
		var points: Array[Vector3]=[]
		# Folded handles meet across the width of three fingers at their crown.
		var profile := PackedVector3Array([Vector3(-.064,.249,.073),Vector3(-.058,.287,.044),Vector3(-.042,.322,.011),Vector3(-.032,.331,.003),Vector3(.032,.331,.003),Vector3(.042,.322,.011),Vector3(.058,.287,.044),Vector3(.064,.249,.073)])
		for k in profile.size():
			var mid:=profile[k]
			var tangent:Vector3=profile[mini(k+1,profile.size()-1)]-profile[maxi(0,k-1)]
			var edge:=Vector3(-tangent.y,tangent.x,0.).normalized()*.0037
			mid.z*=side
			points.append(mid-edge)
			points.append(mid+edge)
		for i in range(profile.size()-1):
			for index in [i*2,i*2+1,i*2+3,i*2,i*2+3,i*2+2]:strip.add_vertex(points[index])
		strip.generate_normals()
		handle.mesh=strip.commit()
		handle.material_override=paper
		add_child(handle)
	var sticker: MeshInstance3D=MeshInstance3D.new()
	var plane: QuadMesh=QuadMesh.new()
	plane.size=Vector2(.16,.087)
	sticker.mesh=plane
	var white: StandardMaterial3D=StandardMaterial3D.new()
	white.albedo_color=Color(.84,.81,.70)
	white.roughness=.96
	sticker.material_override=white
	sticker.position=Vector3(0,.142,.0785)
	add_child(sticker)
	var label: Label3D=Label3D.new()
	label.text="梯坎小面\n一碗热乎 · 路上慢点"
	label.font=load("res://assets/fonts/cq_district_ui.otf")
	label.font_size=32
	label.pixel_size=.0005
	label.modulate=Color(.28,.075,.035)
	label.outline_size=0
	label.position=Vector3(0,.142,.0795)
	add_child(label)
	ticket=label

func write_ticket(number: int,separate_chilli: bool) -> void:
	ticket.font_size=32
	ticket.pixel_size=.0005
	ticket.text="梯坎小面  %03d\n%s" % [number,"小面 · 辣子另装" if separate_chilli else "小面 · 常规"]

func _lathe(part_name: String,profile: Array[Vector2],material: Material,reverse_winding: bool=false) -> void:
	var surface: SurfaceTool=SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var segments: int=40
	for row in range(profile.size()-1):
		for i in range(segments):
			var a: float=TAU*float(i)/segments
			var b: float=TAU*float(i+1)/segments
			var p: Vector2=profile[row]
			var q: Vector2=profile[row+1]
			var vertices: Array[Vector3]=[Vector3(p.x*cos(a),p.y,p.x*sin(a)),Vector3(q.x*cos(a),q.y,q.x*sin(a)),Vector3(q.x*cos(b),q.y,q.x*sin(b)),Vector3(p.x*cos(a),p.y,p.x*sin(a)),Vector3(q.x*cos(b),q.y,q.x*sin(b)),Vector3(p.x*cos(b),p.y,p.x*sin(b))]
			if reverse_winding:vertices.reverse()
			for v in vertices:surface.add_vertex(v)
	surface.generate_normals()
	var part: MeshInstance3D=MeshInstance3D.new()
	part.name=part_name
	part.mesh=surface.commit()
	part.material_override=material
	add_child(part)
