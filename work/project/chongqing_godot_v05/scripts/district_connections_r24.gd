@tool
extends RefCounted
const DONOR := "res://assets/connections_r24/connections.glb"
const PLAN := "res://assets/connections_r24/layout.json"

static func kitchen_finish(source:StandardMaterial3D,kind:int)->ShaderMaterial:
	var finish:=ShaderMaterial.new()
	finish.shader=preload("res://shaders/noodle_surfaces_r24.gdshader")
	finish.set_shader_parameter("finish",kind)
	if kind in [1,2,8]:
		var photo:="old_mosaic_floor" if kind==8 else "interior_tiles"
		var stem:="res://assets/connections_r24/surfaces/"+photo
		finish.set_shader_parameter("floor_photo",load(stem+"_diff_2k.jpg"))
		finish.set_shader_parameter("floor_normal",load(stem+"_nor_gl_2k.jpg"))
		finish.set_shader_parameter("floor_rough",load(stem+"_rough_2k.jpg"))
		if kind==2:
			finish.set_shader_parameter("floor_photo",preload("res://assets/chongqing_district_tile_cream_v4_diff.jpg"))
			finish.set_shader_parameter("floor_normal",preload("res://assets/chongqing_district_tile_cream_v4_nor_gl.jpg"))
			finish.set_shader_parameter("floor_rough",preload("res://assets/chongqing_district_tile_cream_v4_rough.png"))
	finish.set_shader_parameter("tint",source.albedo_color)
	finish.set_shader_parameter("brush",preload("res://assets/characters/serving_counter_r18_CQ_Steel_NORMAL.png"))
	finish.set_shader_parameter("scratches",preload("res://assets/characters/serving_counter_r18_CQ_Steel_ROUGHNESS.png"))
	finish.set_shader_parameter("grain",preload("res://assets/chongqing_district_concrete_floor_worn_001_rough_2k.png"))
	finish.set_shader_parameter("patina",preload("res://assets/chongqing_district_plastered_wall_04_diff_1k.jpg"))
	finish.set_shader_parameter("wood",preload("res://assets/chongqing_district_wood_table_worn_diff_2k.jpg"))
	finish.set_shader_parameter("chilli",preload("res://assets/counter_r21/chilli_station_Fried chilli in rapeseed oil.png"))
	return finish

static func add_visual(city:Node3D,visual:Node3D,editor:bool,preview:Array)->void:
	if editor:
		city.add_child(visual,false,Node.INTERNAL_MODE_BACK)
		preview.append(visual)
	else:
		city.add_child(visual)

static func hide_source(target:MeshInstance3D,prior:Dictionary,originals:Array)->void:
	if not target:return
	RenderingServer.instance_set_visible(target.get_instance(),false)
	originals.append(target)
	var index:int=prior.get("originals",[]).find(target)
	if index>=0:
		var older:MeshInstance3D=prior.drawings[index]
		RenderingServer.instance_set_visible(older.get_instance(),false)

static func install(city:Node3D,editor:=false,prior:Dictionary={},block:Node=null)->Dictionary:
	var originals:=[]
	var drawings:=[]
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	if block:
		for change:Array in plan.get("walk_adjustments",[]):
			block.walking_lanes[change[0]][change[1]][int(change[2])][1]=float(change[3])
	var lib:Node3D=(load(DONOR) as PackedScene).instantiate()
	var grade_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/courtyard_grade/layout.json"))
	var grade:Node3D=(load("res://assets/courtyard_grade/grade.glb") as PackedScene).instantiate()
	var yards_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_age/layout.json"))
	var yards:Node3D=(load("res://assets/district_age/yard.glb") as PackedScene).instantiate()
	var terrace_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/terrace_gardens/layout.json"))
	var terrace:Node3D=(load("res://assets/terrace_gardens/terrace.glb") as PackedScene).instantiate()
	var unit_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_patrol/layout.json"))
	var unit:Node3D=(load("res://assets/district_patrol/district.glb") as PackedScene).instantiate()
	var unit_materials:=preload("res://scripts/unit_interior.gd").finishes()
	unit_materials.merge(preload("res://scripts/blue_stair.gd").finishes())
	var terrace_finishes:=preload("res://scripts/terrace_gardens_r24.gd").finishes()
	var replace:Array=plan.changed.duplicate()
	for key:String in terrace_plan.changed:
		if key not in plan.new and key not in replace:replace.append(key)
	for key:String in yards_plan.changed:
		if not key in plan.new and not key in replace:replace.append(key)
	for key:String in grade_plan.changed:
		if not replace.has(key):replace.append(key)
	for key:String in unit_plan.changed:
		if key not in plan.new and key not in replace:replace.append(key)
	var kitchen_materials:={"steel":0,"duct":0,"kitchenfloor":1,"dado":2,"bamboo":3,"chilioil":4,"oldtile":5,"rice":5,"formica":5,"stoolgreen":5,"celadon":5,"ivory":5,"stove":5,"skirt":5,"brownware":5,"oldstep":8,"noodleplaster":6,"agedtile":5,"workrag":7,"flask":5,"oiljug":5,"paintcream":6,"knob":5,"brine":5,"scallion":5,"broth":5,"jar":5,"redwood":3}
	var cached:={}
	var missing:Array=[]
	var changed:=0
	for key:String in plan.get("retired",[])+grade_plan.retired+yards_plan.retired+unit_plan.retired:
		var obsolete:=city.find_child(key,true,false) as MeshInstance3D
		if editor:hide_source(obsolete,prior,originals)
		elif obsolete:obsolete.mesh=null;obsolete.hide()
	for name_key:String in replace:
		if name_key in grade_plan.retired or name_key in yards_plan.retired or name_key in unit_plan.retired:continue
		var dst:=city.find_child(name_key,true,false) as MeshInstance3D
		var library:=grade if name_key in grade_plan.changed else lib
		if name_key in yards_plan.changed:library=yards
		if name_key in terrace_plan.changed:library=terrace
		if name_key in unit_plan.changed:library=unit
		var src:=library.find_child(name_key,true,false) as MeshInstance3D
		if not src or (not dst and not editor):
			missing.append(name_key)
			continue
		var finishes:Array=[]
		if dst and dst.mesh:
			for i in dst.mesh.get_surface_count():finishes.append(dst.get_active_material(i))
		if editor:
			var actual:=dst.global_transform if dst else city.global_transform*src.transform
			hide_source(dst,prior,originals)
			dst=MeshInstance3D.new()
			add_visual(city,dst,true,drawings)
			dst.global_transform=actual
		dst.mesh=src.mesh
		for i in dst.mesh.get_surface_count():
			var incoming:=dst.mesh.surface_get_material(i)
			if incoming and incoming.resource_name=="Terrace21_floor":
				dst.set_surface_override_material(i,terrace_finishes["Terrace21_floor"])
			elif i<finishes.size():dst.set_surface_override_material(i,finishes[i])
		changed+=1
	var paving:=ShaderMaterial.new()
	paving.shader=preload("res://shaders/joined_stone_r24.gdshader")
	paving.set_shader_parameter("stone",preload("res://assets/chongqing_district_concrete_floor_worn_001_diff_2k.jpg"))
	paving.set_shader_parameter("grain",preload("res://assets/chongqing_district_concrete_floor_worn_001_nor_gl_2k.jpg"))
	var road_paving:=paving.duplicate() as ShaderMaterial
	road_paving.set_shader_parameter("east_shoulder",true)
	road_paving.set_shader_parameter("terrace_grit",preload("res://assets/chongqing_district_concrete_floor_worn_001_nor_gl_2k.jpg"))
	road_paving.set_shader_parameter("terrace_normals",load("res://assets/terrace_gardens/normals.png"))
	road_paving.set_shader_parameter("shoulder_gradient",preload("res://assets/district_age/shoulder_gradient.png"))
	var stone:=paving.duplicate() as ShaderMaterial
	stone.set_shader_parameter("stone",preload("res://assets/district_r21/terraces_washed_sandstone.jpg"))
	stone.set_shader_parameter("grain",preload("res://assets/district_r21/terraces_sandstone_cracks_nor_gl_2k.jpg"))
	stone.set_shader_parameter("tread",true)
	for name_key:String in plan.new:
		var source_lib:=yards if name_key in yards_plan.changed else lib
		if name_key in terrace_plan.changed:source_lib=terrace
		if name_key in unit_plan.changed:source_lib=unit
		var src:=source_lib.find_child(name_key,true,false) as MeshInstance3D
		if not src:missing.append(name_key);continue
		src.owner=null
		src.get_parent().remove_child(src)
		add_visual(city,src,editor,drawings)
		for i in src.mesh.get_surface_count():
			var old:=src.mesh.surface_get_material(i)
			var key:String=old.resource_name.trim_prefix("R18_") if old else ""
			if name_key=="D18_SoupNotice":
				var paper:=StandardMaterial3D.new()
				paper.albedo_texture=load("res://assets/connections_r24/soup_notice.jpg")
				paper.roughness=.88
				src.set_surface_override_material(i,paper)
			elif name_key=="D18_PhotoGinger":
				var skin:=StandardMaterial3D.new()
				skin.albedo_texture=load("res://assets/connections_r24/ginger/food_ginger_01_diff_1k.jpg")
				skin.normal_enabled=true
				skin.normal_texture=load("res://assets/connections_r24/ginger/food_ginger_01_nor_gl_1k.jpg")
				skin.roughness_texture=load("res://assets/connections_r24/ginger/food_ginger_01_rough_1k.jpg")
				src.set_surface_override_material(i,skin)
			elif old is StandardMaterial3D and key in kitchen_materials:
				if not cached.has(key):cached[key]=kitchen_finish(old,kitchen_materials[key])
				src.set_surface_override_material(i,cached[key])
			elif old and old.resource_name=="Terrace21_floor":src.set_surface_override_material(i,terrace_finishes["Terrace21_floor"])
			elif old and old.resource_name=="R18_paver":src.set_surface_override_material(i,road_paving if name_key=="COL_D18_NanquShoulder" else paving)
			elif old and old.resource_name=="R18_stone":src.set_surface_override_material(i,stone)
			elif old is StandardMaterial3D and old.resource_name in ["R18_wall","R18_lime","R18_deepgreen","R18_timber","R18_redwood","R18_cement"]:
				var surface:=old.duplicate() as StandardMaterial3D
				if old.resource_name in ["R18_timber","R18_redwood"]:
					surface.albedo_texture=preload("res://assets/rooms_r24/rooms_timber.jpg")
				else:
					surface.albedo_texture=preload("res://assets/chongqing_district_plastered_wall_04_diff_1k.jpg")
					surface.normal_enabled=true
					surface.normal_texture=preload("res://assets/chongqing_district_plastered_wall_04_nor_gl_1k.jpg")
					surface.normal_scale=.18
				surface.uv1_scale=Vector3(.69,.69,.69)
				src.set_surface_override_material(i,surface)
	for room in plan.rooms:
		var light:=OmniLight3D.new()
		light.light_color=Color(.99,.862,.705) if room.type=="flat" else Color(.97,.914,.79)
		light.light_energy=.29 if room.type=="flat" else .43
		light.omni_range=3.75
		light.distance_fade_enabled=true
		light.distance_fade_begin=16.
		light.distance_fade_length=12.
		add_visual(city,light,editor,drawings)
		light.global_position=Vector3(room.light[0],room.light[1],room.light[2])
	# Only the two uncovered cooking vessels give off vapour. The low draw distance keeps far views free of transparent passes.
	for vent:Vector3 in [Vector3(-22.59,12.556,62.755),Vector3(-23.572,12.398,67.38)]:
		var steam:=MeshInstance3D.new()
		var sheet:=QuadMesh.new()
		sheet.size=Vector2(.39,.43)
		steam.mesh=sheet
		var mist:=ShaderMaterial.new()
		mist.shader=preload("res://shaders/noodle_steam_r24.gdshader")
		mist.set_shader_parameter("phase",vent.x)
		steam.material_override=mist
		steam.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		steam.visibility_range_end=13.
		steam.extra_cull_margin=.42
		add_visual(city,steam,editor,drawings)
		steam.global_position=vent+Vector3.UP*.215
	for place:Vector3 in [Vector3(-22.99,13.61,62.97), Vector3(-24.15,13.48,67.02)]:
		var lamp:=SpotLight3D.new()
		lamp.light_color=Color(.98,.937,.855)
		lamp.light_energy=.68
		lamp.spot_range=3.15
		lamp.spot_angle=58.
		lamp.shadow_enabled=true
		lamp.distance_fade_enabled=true
		lamp.distance_fade_begin=12.
		lamp.distance_fade_length=6.
		add_visual(city,lamp,editor,drawings)
		lamp.global_position=place
		lamp.rotation.x=-PI*.5
	var paper:=StandardMaterial3D.new()
	paper.albedo_texture=preload("res://assets/district_age/wall_prints.png")
	paper.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	paper.roughness=.97
	var painted:=paper.duplicate() as StandardMaterial3D
	painted.albedo_texture=preload("res://assets/district_age/wall_lettering.png")
	var galvanized:={}
	for key:String in yards_plan.new:
		var item:=yards.find_child(key,true,false) as MeshInstance3D
		if not item:missing.append(key);continue
		item.owner=null
		item.get_parent().remove_child(item)
		if key=="COL_Yard20_CornerSurface":
			var original:=city.find_child("COL_Road_734116595_0_asphalt",true,false) as MeshInstance3D
			var asphalt:Material=original.get_active_material(0) if original else null
			var verge:=paving.duplicate() as ShaderMaterial
			verge.set_shader_parameter("yard_paving",true)
			for i in item.mesh.get_surface_count():
				var slot:=item.mesh.surface_get_material(i)
				if slot and "asphalt" in slot.resource_name.to_lower():
					if asphalt:item.set_surface_override_material(i,asphalt)
				else:item.set_surface_override_material(i,verge)
		elif key.begins_with("Yard20_Entry_"):
			item.material_override=paper
			item.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif key.ends_with("Letter"):
			item.material_override=painted
			item.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif key=="Yard20_RoofSheets" or key=="COL_Yard20_BikeShelter":
			for i in item.mesh.get_surface_count():
				var source:=item.get_active_material(i) as StandardMaterial3D
				if not source or source.resource_name.ends_with("anchor"):continue
				if not galvanized.has(source.resource_name):
					var metal:=ShaderMaterial.new()
					metal.shader=preload("res://shaders/yard_galvanized.gdshader")
					metal.set_shader_parameter("coat",source.albedo_color)
					metal.set_shader_parameter("paint_scan",preload("res://assets/chongqing_district_rusty_painted_metal_diff_2k.jpg"))
					galvanized[source.resource_name]=metal
				item.set_surface_override_material(i,galvanized[source.resource_name])
		elif key.begins_with("COLH_"):item.visible=false
		add_visual(city,item,editor,drawings)
	for key:String in terrace_plan.new:
		var item:=terrace.find_child(key,true,false) as MeshInstance3D
		if not item:missing.append(key);continue
		item.owner=null
		item.get_parent().remove_child(item)
		for i in item.mesh.get_surface_count():
			var slot:=item.mesh.surface_get_material(i)
			if slot and terrace_finishes.has(slot.resource_name):item.set_surface_override_material(i,terrace_finishes[slot.resource_name])
		if key.begins_with("COLH_"):item.hide()
		add_visual(city,item,editor,drawings)
	var gardens:=Node3D.new()
	gardens.name="TerraceGardens"
	add_visual(city,gardens,editor,drawings)
	preload("res://scripts/terrace_gardens_r24.gd").add_plants(city,gardens,terrace_plan.plants,missing)
	for key:String in unit_plan.new:
		var part:=unit.find_child(key,true,false) as MeshInstance3D
		if not part:missing.append(key);continue
		part.owner=null
		part.get_parent().remove_child(part)
		add_visual(city,part,editor,drawings)
		if key.begins_with("COLH_"):part.hide()
		if key in ["COL_Patrol25_StationRear","COL_Patrol25_EastLane"]:
			var ground:=city.find_child("COL_Terrain_200m_yard_concrete",true,false) as MeshInstance3D
			if ground:part.material_override=ground.get_active_material(0)
		if key=="COL_Patrol25_CourtBank":
			var masonry:=ShaderMaterial.new()
			masonry.shader=preload("res://shaders/court_bank.gdshader")
			masonry.set_shader_parameter("mineral",preload("res://assets/chongqing_district_stone_wall_05_diff_2k.jpg"))
			part.material_override=masonry
		for i in part.mesh.get_surface_count():
			var mat:=part.mesh.surface_get_material(i)
			if key in ["COL_Patrol25_TurnLandings","COL_Patrol25_LowerLanding","COL_Patrol25_CentralLanding","COL_Patrol25_UpperLanding"]:
				var slab:=preload("res://scripts/lane_connection_r24.gd").paver(true)
				slab.set_shader_parameter("cement",preload("res://assets/district_r21/terraces_washed_sandstone.jpg"))
				var tint:=Vector3(.68,.61,.52) if key=="COL_Patrol25_TurnLandings" else Vector3(.46,.407,.342)
				slab.set_shader_parameter("stone_tint",tint)
				part.set_surface_override_material(i,slab)
				continue
			if not mat or not unit_materials.has(mat.resource_name):continue
			var finish:StandardMaterial3D=unit_materials[mat.resource_name]
			if key=="COL_Unit22_BackGallery" and mat.resource_name in ["R18_unit22_tread","R18_unit22_edge"]:
				finish=finish.duplicate() as StandardMaterial3D
				finish.albedo_color=Color("f1efdf")
				finish.albedo_texture=preload("res://assets/district_r21/terraces_washed_sandstone.jpg")
				finish.normal_texture=preload("res://assets/district_r21/terraces_sandstone_cracks_nor_gl_2k.jpg")
				finish.normal_scale=.24
			part.set_surface_override_material(i,finish)
	var common:=Node3D.new()
	common.name="UnitOne"
	add_visual(city,common,editor,drawings)
	preload("res://scripts/unit_interior.gd").furnish(common)
	preload("res://scripts/blue_stair.gd").furnish(common)
	var court:=city.find_child("COL_Community_court_pavement",true,false) as MeshInstance3D
	if court:
		var paint:=ShaderMaterial.new()
		paint.shader=preload("res://shaders/court_paint_r24.gdshader")
		paint.set_shader_parameter("concrete",preload("res://assets/chongqing_district_concrete_floor_worn_001_diff_2k.jpg"))
		if editor:
			var proxy:=MeshInstance3D.new()
			proxy.mesh=court.mesh
			add_visual(city,proxy,true,drawings)
			proxy.global_transform=court.global_transform
			hide_source(court,prior,originals)
			court=proxy
		court.material_override=paint
	unit.free()
	terrace.free()
	yards.free()
	grade.free()
	lib.free()
	if editor:return {"originals":originals,"drawings":drawings,"changed":changed,"missing":missing}
	return {"terrace_beds":terrace_plan.beds,"terrace_plants":terrace_plan.plants.size(),"terrace_sha256":FileAccess.get_sha256("res://assets/terrace_gardens/terrace.glb"),"yards_new":yards_plan.new,"yards_ground":yards_plan.retired,"yard_donor_sha256":FileAccess.get_sha256("res://assets/district_age/yard.glb"),"changed":changed,"missing":missing,"new":plan.new.size(),"rooms":plan.rooms.size(),"retired_stair_grates":plan.drains.size(),"single_surface_changed":grade_plan.changed.size(),"retired_ground":grade_plan.retired,"grade_donor_sha256":FileAccess.get_sha256("res://assets/courtyard_grade/grade.glb")}
