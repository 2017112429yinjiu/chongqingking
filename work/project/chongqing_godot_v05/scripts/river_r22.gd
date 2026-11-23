extends Node3D

const MODEL := "res://assets/river_r22/river_context.glb"
const PLAN := "res://assets/river_r22/layout.json"
var fleet: Array = []
var elapsed := 0.0

func install(city: Node3D) -> Dictionary:
	name = "RiverContextR22"
	city.add_child(self)
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	var layer := (load(MODEL) as PackedScene).instantiate() as Node3D
	add_child(layer)
	for donor: String in spec.terrain:
		var old := city.find_child(donor,true,false) as MeshInstance3D
		var bank := layer.find_child(spec.terrain[donor].replacement,true,false) as MeshInstance3D
		var sediment:=ShaderMaterial.new()
		sediment.shader=preload("res://shaders/riverbank_r22.gdshader")
		sediment.set_shader_parameter("shore",load("res://assets/river_r22/shore_masks.png"))
		sediment.set_shader_parameter("gravel",load("res://assets/chongqing_district_leaf_scattered_gravel_diff_2k.jpg"))
		sediment.set_shader_parameter("mud",load("res://assets/chongqing_district_brown_mud_leaves_01_diff_2k.jpg"))
		if donor=="Outer_ground_context_ground_dirt":
			var previous:=old.get_active_material(0) as ShaderMaterial
			sediment.set_shader_parameter("outer_ground",true)
			for key in ["land","tree_shade","paving"]:
				sediment.set_shader_parameter(key,previous.get_shader_parameter(key))
		bank.set_surface_override_material(0,sediment)
		if donor=="R19_Distant_relief_distant19":
			var bar:=layer.find_child("R22_Sandbar",true,false) as MeshInstance3D
			var sand:=sediment.duplicate() as ShaderMaterial
			sand.set_shader_parameter("shoal",true)
			bar.set_surface_override_material(0,sand)
		bank.cast_shadow=old.cast_shadow
		old.visible=false
	var water:=layer.find_child("R22_Water_sheet_river",true,false) as MeshInstance3D
	var river_material:=ShaderMaterial.new()
	river_material.shader=preload("res://shaders/river_r22.gdshader")
	water.set_surface_override_material(0,river_material)
	water.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var grove:=layer.find_child("R22_Riparian_groves",true,false) as MeshInstance3D
	var leaf:=ShaderMaterial.new()
	leaf.shader=preload("res://shaders/river_foliage_r22.gdshader")
	leaf.set_shader_parameter("atlas",load("res://assets/district_r21/canopy_atlas.png"))
	grove.set_surface_override_material(0,leaf)
	grove.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for vehicle: Dictionary in spec.vehicles:
		var axis: Dictionary=spec.axes[vehicle.axis]
		var from:=Vector3(axis.north[0],axis.north[1],axis.north[2])
		var to:=Vector3(axis.south[0],axis.south[1],axis.south[2])
		var actor:=layer.find_child(vehicle.node,true,false) as Node3D
		fleet.append({"actor":actor,"from":from,"to":to,"length":float(axis.length),
			"reverse":vehicle.reverse,"phase":float(vehicle.phase),"speed":float(vehicle.speed_m_s),
			"crown":float(axis.deck_crown_m)})
		actor.basis=Basis.looking_at((from-to if vehicle.reverse else to-from).normalized(),Vector3.UP)
	update_traffic(0.)
	return {"layer_sha256":FileAccess.get_sha256(MODEL),"layout_sha256":FileAccess.get_sha256(PLAN),
		"source_plan_sha256":spec.source_plan_sha256,"axes":spec.axes.size(),"fleet":fleet.size(),
		"mapped_buildings":spec.mapped_buildings.size(),"terrain":spec.terrain}

func update_traffic(seconds: float) -> void:
	for item: Dictionary in fleet:
		var phase:=fposmod(float(item.phase)+seconds*float(item.speed)/float(item.length),1.)
		var t:=1.-phase if item.reverse else phase
		var node:=item.actor as Node3D
		var origin: Vector3=item.from
		node.position=origin.lerp(item.to,t)+Vector3.UP*float(item.crown)*sin(PI*t)
		node.visible=phase>.012 and phase<.988

func _process(delta: float) -> void:
	elapsed+=delta
	update_traffic(elapsed)
