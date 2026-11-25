extends RefCounted
const LAYOUT:="res://assets/district_r21/layout.json"
const MODEL:="res://assets/district_r21/terraces.glb"

static func point(a: Array) -> Vector3:
	return Vector3(a[0],a[1],a[2])

static func install(city: Node3D, planted_extent_m: float = 0.0) -> Dictionary:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	var group:=Node3D.new()
	group.name="DistrictEnvironmentR21"
	city.add_child(group)
	var masonry:=load(MODEL).instantiate() as Node3D
	group.add_child(masonry)
	var donors: Dictionary={}
	for index in data.trees_and_shrubs.size():
		var spec: Dictionary=data.trees_and_shrubs[index]
		for label: String in spec.donors:
			if not donors.has(label):donors[label]=city.find_child(label,true,false) as MeshInstance3D
			var original:=donors[label] as MeshInstance3D
			assert(original!=null,label)
			var part:=MeshInstance3D.new()
			part.name="Plant_%02d_%s"%[index,label]
			part.mesh=original.mesh
			part.lod_bias=original.lod_bias
			for i in original.get_surface_override_material_count():
				part.set_surface_override_material(i,original.get_surface_override_material(i))
			part.transform=Transform3D(Basis(Vector3.UP,spec.yaw).scaled(Vector3.ONE*float(spec.scale)),point(spec.position))
			group.add_child(part)
		if spec.trunk:
			var body:=StaticBody3D.new()
			body.name="Trunk_%02d"%index
			group.add_child(body)
			body.position=point(spec.position)
			var cylinder:=CylinderShape3D.new()
			cylinder.radius=.027*float(spec.height)
			cylinder.height=2.45
			var shape:=CollisionShape3D.new()
			shape.shape=cylinder
			body.add_child(shape)
			shape.position.y=cylinder.height*.5
	var background: Array = data.outer_canopy
	if planted_extent_m > 0.0:
		background = background.filter(func(tree: Dictionary):
			var p := point(tree.position)
			return maxf(absf(p.x), absf(p.z)) > planted_extent_m)
	var exterior_sectors := install_canopy(group, background, data.canopy_pivots, 62.0)
	var paving:=ShaderMaterial.new()
	paving.shader=preload("res://shaders/paving_r21.gdshader")
	paving.set_shader_parameter("worn_floor",load("res://assets/street_r19/street_life_concrete_floor_worn_001_diff_2k.jpg"))
	paving.set_shader_parameter("floor_normal",load("res://assets/street_r19/street_life_concrete_floor_worn_001_nor_gl_2k.jpg"))
	paving.set_shader_parameter("shop_sky",load("res://assets/lane_r20/shop_sky.png"))
	paving.set_shader_parameter("alley_sky",load("res://assets/lane_r20/alley_sky.png"))
	var stair:=paving.duplicate() as ShaderMaterial
	stair.set_shader_parameter("stairs",true)
	var changed: Array[String]=[]
	var fields: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/wall_fields.json"))
	var weather:=load("res://assets/district_r21/wall_runoff.png") as Texture2D
	var treatments: Dictionary={}
	var weathered_surfaces:=0
	var worn_rail:=ShaderMaterial.new()
	worn_rail.shader=preload("res://shaders/worn_rail_r21.gdshader")
	var exterior:=ShaderMaterial.new()
	exterior.shader=preload("res://shaders/exterior_r21.gdshader")
	exterior.set_shader_parameter("land",load("res://assets/district_r21/exterior_land.png"))
	exterior.set_shader_parameter("tree_shade",load("res://assets/district_r21/exterior_sun_mask.png"))
	exterior.set_shader_parameter("earth",load("res://assets/chongqing_district_brown_mud_leaves_01_diff_2k.jpg"))
	exterior.set_shader_parameter("paving",load("res://assets/street_r19/street_life_concrete_floor_worn_001_diff_2k.jpg"))
	for mesh: MeshInstance3D in city.find_children("*","MeshInstance3D",true,false):
		var label:=String(mesh.name)
		if label.begins_with("COL_B_"):
			var building:=label.get_slice("_",2)
			if fields.buildings.has(building):
				var field: Dictionary=fields.buildings[building]
				for i in mesh.get_surface_override_material_count():
					var original:=mesh.get_surface_override_material(i) as ShaderMaterial
					if original==null or not original.resource_name.begins_with("R19_"):continue
					var key:=building+"_"+str(original.get_instance_id())
					if not treatments.has(key):
						var finish:=original.duplicate() as ShaderMaterial
						finish.set_shader_parameter("use_facade_weather",true)
						finish.set_shader_parameter("weather_atlas",weather)
						finish.set_shader_parameter("weather_grid",Vector2(fields.atlas_grid[0],fields.atlas_grid[1]))
						finish.set_shader_parameter("facade_low",point(field.min))
						finish.set_shader_parameter("facade_span",point(field.span))
						finish.set_shader_parameter("first_weather_tile",float(field.first_tile))
						treatments[key]=finish
					mesh.set_surface_override_material(i,treatments[key])
					weathered_surfaces+=1
		if label=="Outer_ground_context_ground_dirt":
			mesh.set_surface_override_material(0,exterior)
			changed.append(label)
		elif label=="COL_Terrain_200m_yard_concrete" or label=="R20_Court_paving_step_concrete":
			mesh.set_surface_override_material(0,paving)
			changed.append(label)
		elif label=="R19_Stair_tread_caps_step_concrete" and data.has("stonework"):
			mesh.visible=false
		elif (label.begins_with("COL_Handrails_") or label.begins_with("Walk_details_OSM_")) and label.ends_with("painted_metal"):
			mesh.set_surface_override_material(0,worn_rail)
			changed.append(label)
		elif label.begins_with("COL_Walk_") and label.ends_with("step_concrete"):
			mesh.set_surface_override_material(0,stair)
			changed.append(label)
	return {"layout_sha256":FileAccess.get_sha256(LAYOUT),"layer_sha256":FileAccess.get_sha256(MODEL),"paving":changed,"weathered_shell_surfaces":weathered_surfaces,"weather_atlas_sha256":FileAccess.get_sha256("res://assets/district_r21/wall_runoff.png"),"near_plantings":data.trees_and_shrubs.size(),"exterior_trees":background.size(),"exterior_sectors":exterior_sectors,"terraces":data.terraces.size(),"roof_structures":data.rooftops.size(),"window_fittings":data.get("facades",[]).size()}

static func install_canopy(group: Node3D, trees: Array, pivots: Dictionary, cell_size: float, begin_distance: float = 0.0) -> int:
	var sectors: Dictionary={}
	var plane:=QuadMesh.new()
	plane.size=Vector2.ONE
	plane.center_offset=Vector3(0,.48,0)
	var leaves:=ShaderMaterial.new()
	leaves.shader=preload("res://shaders/canopy_r21.gdshader")
	leaves.set_shader_parameter("atlas",load("res://assets/district_r21/canopy_atlas.png"))
	plane.material=leaves
	for tree: Dictionary in trees:
		var pos:=point(tree.position)
		var cell:=Vector2i(floori(pos.x/cell_size),floori(pos.z/cell_size))
		if not sectors.has(cell):sectors[cell]=[]
		sectors[cell].append(tree)
	for cell: Vector2i in sectors:
		var plants: Array=sectors[cell]
		var batch:=MultiMesh.new()
		batch.transform_format=MultiMesh.TRANSFORM_3D
		batch.use_custom_data=true
		batch.mesh=plane
		batch.instance_count=plants.size()
		var min_bound:=Vector3(INF,INF,INF)
		var max_bound:=-min_bound
		for i in plants.size():
			var tree: Dictionary=plants[i]
			var kind: String="tree_small_02" if tree.kind==0 else "island_tree_01"
			var width: float=tree.height*pivots[kind].frame_width_over_height
			var pos:=point(tree.position)
			batch.set_instance_transform(i,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*width),pos))
			batch.set_instance_custom_data(i,Color(fposmod(float(tree.yaw)/TAU,1.),float(tree.kind),float(tree.shade),1.))
			min_bound=min_bound.min(pos-Vector3(width*.71,width*.04,width*.71))
			max_bound=max_bound.max(pos+Vector3(width*.71,width,width*.71))
		var patch:=MultiMeshInstance3D.new()
		patch.name="Hillside_%d_%d"%[cell.x,cell.y]
		patch.visibility_range_begin = begin_distance
		patch.multimesh=batch
		patch.custom_aabb=AABB(min_bound,max_bound-min_bound)
		patch.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		group.add_child(patch)
	return sectors.size()
