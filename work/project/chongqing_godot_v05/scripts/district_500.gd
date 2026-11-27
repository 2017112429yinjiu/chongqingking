extends RefCounted

const MODEL := "res://assets/district_500/outer_district.glb"
const LAYOUT := "res://assets/district_500/layout.json"
const INTERIOR_TERRAIN := "res://assets/district_500/interior_terrain.json"
const RIVERSIDE := "res://assets/district_500/riverside.glb"
const MATCH_FACTORY := "res://assets/district_500/match_factory.glb"
const MATCH_FACTORY_SITE := "res://assets/district_500/match_factory.json"
const MATIX_STREETS := "res://assets/district_500/matix_streets.glb"
const MATIX_SITE := "res://assets/district_500/matix_streets.json"
const ZHONGXING_WALL := "res://assets/district_500/zhongxing-retaining.glb"
const ZHONGXING_SITE := "res://assets/district_500/zhongxing-retaining.json"
const WEST_COURT := "res://assets/district_500/west-court.glb"
const WEST_COURT_SITE := "res://assets/district_500/west-court.json"
const WEST_RAMP := "res://assets/district_500/west-ramp.glb"
const WEST_RAMP_SITE := "res://assets/district_500/west-ramp.json"
const GUOCO := "res://assets/district_500/guoco-frontages.glb"
const GUOCO_SITE := "res://assets/district_500/guoco-frontages.json"
const HOUCI := "res://assets/district_500/houci-77.glb"
const HOUCI_SITE := "res://assets/district_500/houci-77.json"
const PANDA := "res://assets/district_500/panda-15-17.glb"
const PANDA_SITE := "res://assets/district_500/panda-15-17.json"
const ZHONGXING_BRIDGE := "res://assets/district_500/zhongxing-bridge-18-21.glb"
const ZHONGXING_BRIDGE_SITE := "res://assets/district_500/zhongxing-bridge-18-21.json"
const HOUCI_CONNECTORS := "res://assets/district_500/houci-14-16.glb"
const HOUCI_CONNECTORS_SITE := "res://assets/district_500/houci-14-16.json"
const FENGHUANGTAI_11 := "res://assets/district_500/fenghuangtai-11.glb"
const FENGHUANGTAI_11_SITE := "res://assets/district_500/fenghuangtai-11.json"
const CHANGBIN_55 := "res://assets/district_500/changbin-55.glb"
const CHANGBIN_55_SITE := "res://assets/district_500/changbin-55.json"
const NORTH_EDGES := "res://assets/district_500/north-38-40-41.glb"
const NORTH_EDGES_SITE := "res://assets/district_500/north-38-40-41.json"
const LIANGTINGZI := "res://assets/district_500/liangtingzi-45-46.glb"
const LIANGTINGZI_SITE := "res://assets/district_500/liangtingzi-45-46.json"
const MATI34_35 := "res://assets/district_500/mati-34-35.glb"
const MATI34_35_SITE := "res://assets/district_500/mati-34-35.json"
const ZHONGXING_PUBLIC_EDGES := "res://assets/district_500/zhongxing-public-10-12-13-22.glb"
const ZHONGXING_PUBLIC_EDGES_SITE := "res://assets/district_500/zhongxing-public-10-12-13-22.json"
const NANQU := "res://assets/district_500/nanqu-04-06-51.glb"
const NANQU_SITE := "res://assets/district_500/nanqu-04-06-51.json"
const WILDERNESS_50 := "res://assets/district_500/wilderness-50.glb"
const WILDERNESS_50_SITE := "res://assets/district_500/wilderness-50.json"
const WILDERNESS_FINISH := "res://assets/district_500/wilderness-50-finish.glb"
const WILDERNESS_FINISH_SITE := "res://assets/district_500/wilderness-50-finish.json"
const PUBLIC_EDGES := "res://assets/district_500/public-edges.glb"
const PUBLIC_EDGES_SITE := "res://assets/district_500/public-edges.json"
const XINGCHEN := "res://assets/district_500/xingchen.glb"
const XINGCHEN_SITE := "res://assets/district_500/xingchen.json"
const PAVILION_62 := "res://assets/district_500/pavilion62.glb"
const PAVILION_62_SITE := "res://assets/district_500/pavilion62.json"
const COLLECTIBLES := "res://assets/district_500/collectibles-market.glb"
const COLLECTIBLES_SITE := "res://assets/district_500/collectibles-market.json"
const MARKET_STALL_ROW := "res://assets/district_500/market-stall-row.glb"
const MARKET_STALL_ROW_SITE := "res://assets/district_500/market-stall-row.json"
const PARK_PLOT_57 := "res://assets/district_500/park-plot57.glb"
const PARK_PLOT_57_SITE := "res://assets/district_500/park-plot57.json"
const BRIDGE_PARK := "res://assets/district_500/bridge-park.glb"
const BRIDGE_PARK_SITE := "res://assets/district_500/bridge-park.json"
const PARK_PLOT_59 := "res://assets/district_500/park-plot59.glb"
const PARK_PLOT_59_SITE := "res://assets/district_500/park-plot59.json"
const PARK_PLOT_61 := "res://assets/district_500/park-plot61.glb"
const PARK_PLOT_61_SITE := "res://assets/district_500/park-plot61.json"
const PARK_EDGE_FINISH := "res://assets/district_500/park-edge-finish.glb"
const PARK_EDGE_FINISH_SITE := "res://assets/district_500/park-edge-finish.json"
const CHANGBIN_BEND := "res://assets/district_500/changbin-bend-and-edge.glb"
const CHANGBIN_BEND_SITE := "res://assets/district_500/changbin-bend-and-edge.json"
const RAIJIAPO_EAST := "res://assets/district_500/raijiapo-east-bend.glb"
const RAIJIAPO_EAST_SITE := "res://assets/district_500/raijiapo-east-bend.json"
const BINJIANG := "res://assets/district_500/binjiang-70-73.glb"
const BINJIANG_SITE := "res://assets/district_500/binjiang-70-73.json"

static func north_edge_mode() -> String:
	for id: String in ["10","12","13","22","34","35","38","40","41","45","46"]:
		if ("--north-edge="+id) in OS.get_cmdline_user_args():
			return id
	return ""


static func install(city: Node3D) -> Dictionary:
	var district := (load(MODEL) as PackedScene).instantiate() as Node3D
	district.name = "OuterDistrict500"
	var correction: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INTERIOR_TERRAIN))
	var mesh_layer := (load("res://assets/district_500/interior_terrain.glb") as PackedScene).instantiate()
	for mesh_name: String in correction.tiles_and_wall:
		var original := district.find_child(mesh_name, true, false) as MeshInstance3D
		var replacement := mesh_layer.find_child(mesh_name, true, false) as MeshInstance3D
		assert(original and replacement, mesh_name)
		original.mesh = replacement.mesh
	mesh_layer.free()
	var relocated: Array = correction.tree_east_north_up
	var tree_mesh := district.find_child("Outer500_Plant_036", true, false) as MeshInstance3D
	tree_mesh.position = enu(relocated)
	city.add_child(district)
	var low_landing := (load("res://assets/district_500/landing_53.glb") as PackedScene).instantiate() as Node3D
	district.add_child(low_landing)
	var mapped_lane: PackedScene=load("res://assets/district_500/shancheng_lane.glb")
	district.add_child(mapped_lane.instantiate())
	var historic_courts := load("res://assets/district_500/historic_courts.glb") as PackedScene
	district.add_child(historic_courts.instantiate())
	var riverside := (load(RIVERSIDE) as PackedScene).instantiate()
	riverside.name = "RiversideWalk"
	district.add_child(riverside)
	var guoco_plant_roots: Array = []
	var xingchen_way: Array = []
	var market_ways: Array = []
	var retired_bridge_plots: Array = []
	if not "--qa-without-match-factory" in OS.get_cmdline_user_args():
		install_street_group(district, MATCH_FACTORY, MATCH_FACTORY_SITE, "MatchFactory")
		if not "--qa-without-matix-streets" in OS.get_cmdline_user_args():
			install_street_group(district, MATIX_STREETS, MATIX_SITE, "MatixStreets")
			install_street_group(district, ZHONGXING_WALL, ZHONGXING_SITE, "ZhongxingStreetWall")
			install_street_group(district, WEST_COURT, WEST_COURT_SITE, "RiversideWestCourt")
			if not "--qa-without-west-ramp" in OS.get_cmdline_user_args():
				install_street_group(district, WEST_RAMP, WEST_RAMP_SITE, "WestCourtRampFinish")
			if not "--qa-without-guoco" in OS.get_cmdline_user_args():
				install_street_group(district, GUOCO, GUOCO_SITE, "GuocoFrontages")
				var guoco: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(GUOCO_SITE))
				guoco_plant_roots = guoco.retired_roots_east_north
				if not "--qa-without-public-edges" in OS.get_cmdline_user_args():
					install_street_group(district, PUBLIC_EDGES, PUBLIC_EDGES_SITE, "PublicEdges")
					if not "--qa-without-xingchen" in OS.get_cmdline_user_args():
						install_street_group(district, XINGCHEN, XINGCHEN_SITE, "Xingchen")
						var site: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(XINGCHEN_SITE))
						xingchen_way.append(int(site.way))
						if not "--qa-without-pavilion62" in OS.get_cmdline_user_args():
							install_street_group(district, PAVILION_62, PAVILION_62_SITE, "RiversidePavilion62")
							if not "--qa-without-collectibles" in OS.get_cmdline_user_args():
								install_street_group(district, COLLECTIBLES, COLLECTIBLES_SITE, "ZhongxingCollectiblesMarket")
								var market: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(COLLECTIBLES_SITE))
								market_ways = market.mapped_residential_ways
								add_collectibles_details(district, market)
								if not "--qa-without-market-stall-row" in OS.get_cmdline_user_args():
									install_street_group(district, MARKET_STALL_ROW, MARKET_STALL_ROW_SITE, "ZhongxingMarketEastStalls")
								if not "--qa-without-west-ramp" in OS.get_cmdline_user_args() and not "--qa-without-park-plot57" in OS.get_cmdline_user_args():
									install_street_group(district, PARK_PLOT_57, PARK_PLOT_57_SITE, "RiversideParkPlot57")
									if not "--qa-without-bridge-park" in OS.get_cmdline_user_args():
										install_street_group(district, BRIDGE_PARK, BRIDGE_PARK_SITE, "NanjimenBridgePark")
										var bridge: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BRIDGE_PARK_SITE))
										retired_bridge_plots = bridge.parking.retired_trial_plots
										if not "--qa-without-park-plot59" in OS.get_cmdline_user_args():
											install_street_group(district, PARK_PLOT_59, PARK_PLOT_59_SITE, "RiversideParkPlot59")
											var park: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PARK_PLOT_59_SITE))
											retired_bridge_plots.append(park.replaced_plot)
											if not "--qa-without-park-plot61" in OS.get_cmdline_user_args():
												install_street_group(district, PARK_PLOT_61, PARK_PLOT_61_SITE, "RiversideParkPlot61")
												var edge_park: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PARK_PLOT_61_SITE))
												retired_bridge_plots.append(edge_park.replaced_plot)
												if not "--qa-without-park-edge-finish" in OS.get_cmdline_user_args():
													install_street_group(district, PARK_EDGE_FINISH, PARK_EDGE_FINISH_SITE, "RiversideParkEdgeFinish")
													finish_park_trees(district)
													if not "--qa-without-changbin-bend" in OS.get_cmdline_user_args():
														install_street_group(district, CHANGBIN_BEND, CHANGBIN_BEND_SITE, "ChangbinBendAndParkEdge")
														var changbin: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CHANGBIN_BEND_SITE))
														retired_bridge_plots.append_array(changbin.retired_plots)
														if not "--qa-without-raijiapo-east" in OS.get_cmdline_user_args():
															install_street_group(district, RAIJIAPO_EAST, RAIJIAPO_EAST_SITE, "RaijiapoEastBend")
															var east: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RAIJIAPO_EAST_SITE))
															retired_bridge_plots.append_array(east.retired_plots)
															place_east_tree(district,east.tree)
															if not "--qa-without-binjiang" in OS.get_cmdline_user_args():
																install_street_group(district, BINJIANG, BINJIANG_SITE, "BinjiangFrontages")
																var binjiang := load_binjiang_plan()
																retired_bridge_plots.append_array(binjiang.retired_plots)
																hide_replaced_binjiang_facades(city,binjiang.retired_runtime_frontage)
	var houci_active := district.has_node("BinjiangFrontages") and not "--qa-without-houci-77" in OS.get_cmdline_user_args()
	if houci_active:
		install_street_group(district, HOUCI, HOUCI_SITE, "HouciStreet77")
		retired_bridge_plots.append(77)
	var panda_active := houci_active and not "--qa-without-panda-frontage" in OS.get_cmdline_user_args()
	if panda_active:
		install_street_group(district, PANDA, PANDA_SITE, "PandaPublicFrontage")
		var panda: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PANDA_SITE))
		retired_bridge_plots.append_array(panda.retired_plots)
		var frontage := district.get_node("PandaPublicFrontage")
		for spec: Dictionary in panda.trees:
			var donor := district.find_child(spec.donor, true, false) as MeshInstance3D
			var tree := donor.duplicate() as MeshInstance3D
			tree.name = spec.name
			tree.position = enu(spec.enu)
			tree.rotation.y += spec.yaw
			tree.scale *= spec.scale
			frontage.add_child(tree)
		var site_font := SystemFont.new()
		site_font.font_names = PackedStringArray(["Noto Sans CJK SC", "Microsoft YaHei"])
		var landmark := Label3D.new()
		landmark.name = "PandaArcadeName"
		landmark.text = panda.portal_sign.get("text", "熊猫古玩文化金街")
		landmark.font = site_font
		landmark.font_size = 62
		landmark.pixel_size = .006
		landmark.modulate = Color("#ead9bf")
		landmark.outline_size = 1
		landmark.position = enu(panda.portal_sign.enu)
		landmark.rotation.y = panda.portal_sign.yaw
		frontage.add_child(landmark)
		for spec: Dictionary in panda.get("visual_signs", []):
			var board := Label3D.new()
			board.text = spec.text
			board.font = site_font
			board.font_size = 60
			board.pixel_size = spec.pixel_size
			board.modulate = Color(spec.color)
			board.outline_size = 1
			board.position = enu(spec.enu)
			board.rotation.y = panda.portal_sign.yaw
			frontage.add_child(board)
	var bridge_margins_active := panda_active and not "--qa-without-zhongxing-18-21" in OS.get_cmdline_user_args()
	if bridge_margins_active:
		install_street_group(district, ZHONGXING_BRIDGE, ZHONGXING_BRIDGE_SITE, "ZhongxingBridgeMargins")
		var bridge_margins: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ZHONGXING_BRIDGE_SITE))
		retired_bridge_plots.append_array(bridge_margins.retired_plots)
	var connectors_active := bridge_margins_active and not "--qa-without-houci-14-16" in OS.get_cmdline_user_args()
	if connectors_active:
		install_street_group(district, HOUCI_CONNECTORS, HOUCI_CONNECTORS_SITE, "HouciConnectors1416")
		var connectors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(HOUCI_CONNECTORS_SITE))
		retired_bridge_plots.append_array(connectors.retired_plots)
	var lower_junction_active := connectors_active and not "--qa-without-fenghuangtai-11" in OS.get_cmdline_user_args()
	if lower_junction_active:
		install_street_group(district, FENGHUANGTAI_11, FENGHUANGTAI_11_SITE, "FenghuangtaiLowerJunction")
		var junction: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FENGHUANGTAI_11_SITE))
		retired_bridge_plots.append_array(junction.retired_plots)
	var wilderness_active := lower_junction_active and not "--qa-without-wilderness-50" in OS.get_cmdline_user_args()
	if wilderness_active:
		install_street_group(district, WILDERNESS_50, WILDERNESS_50_SITE, "RenaiGardenRelicEdge")
		var garden_edge: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WILDERNESS_50_SITE))
		retired_bridge_plots.append_array(garden_edge.retired_plots)
	var wilderness_finish_active := wilderness_active and not "--qa-without-wilderness-50-finish" in OS.get_cmdline_user_args()
	if wilderness_finish_active:
		install_street_group(district, WILDERNESS_FINISH, WILDERNESS_FINISH_SITE, "RenaiGardenPublicFinish")
	var nanqu_active := wilderness_active and not "--qa-without-nanqu-04-06-51" in OS.get_cmdline_user_args()
	var nanqu_rebased_trees := {}
	var nanqu_retired_meshes: Array=[]
	if nanqu_active:
		install_street_group(district, NANQU, NANQU_SITE, "NanquRiverFootway")
		var nanqu: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(NANQU_SITE))
		retired_bridge_plots.append_array(nanqu.retired_plots)
		nanqu_retired_meshes=nanqu.retired_objects
		for spec: Dictionary in nanqu.get("rebase_trees",[]):
			var plant := district.find_child(spec.name,true,false) as Node3D
			assert(plant,spec.name)
			plant.position.y += float(spec.shift_z)
			nanqu_rebased_trees[spec.name]=plant.position.y
	var changbin55_active := nanqu_active and not "--qa-without-changbin-55" in OS.get_cmdline_user_args()
	if changbin55_active:
		install_street_group(district, CHANGBIN_55, CHANGBIN_55_SITE, "ChangbinRoadShoulder55")
		var roadside: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CHANGBIN_55_SITE))
		retired_bridge_plots.append_array(roadside.retired_plots)
	var north_active := changbin55_active and not "--qa-without-north-edges" in OS.get_cmdline_user_args()
	if north_active:
		install_street_group(district, NORTH_EDGES, NORTH_EDGES_SITE, "NorthPublicEdges")
		var north: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(NORTH_EDGES_SITE))
		retired_bridge_plots.append_array(north.retired_plots)
	var liangtingzi_active := north_active and not "--qa-without-liangtingzi-45-46" in OS.get_cmdline_user_args()
	if liangtingzi_active:
		install_street_group(district, LIANGTINGZI, LIANGTINGZI_SITE, "LiangtingziPublicEdges")
		var liangtingzi: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LIANGTINGZI_SITE))
		add_public_edge_trees(district, district.get_node("LiangtingziPublicEdges"), liangtingzi.get("trees", []))
	var mati34_active := liangtingzi_active and not "--qa-without-mati-34-35" in OS.get_cmdline_user_args()
	if mati34_active:
		install_street_group(district, MATI34_35, MATI34_35_SITE, "Mati34And35PublicEdges")
	var zhongxing_public_active := mati34_active and not "--qa-without-zhongxing-public-edges" in OS.get_cmdline_user_args()
	if zhongxing_public_active:
		install_street_group(district, ZHONGXING_PUBLIC_EDGES, ZHONGXING_PUBLIC_EDGES_SITE, "ZhongxingPublicEdges")
		var plaza: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ZHONGXING_PUBLIC_EDGES_SITE))
		retired_bridge_plots.append_array(plaza.retired_plots)
		add_public_edge_trees(district, district.get_node("ZhongxingPublicEdges"), plaza.trees)
	var ground := ShaderMaterial.new()
	ground.shader = preload("res://shaders/district_500_ground.gdshader")
	ground.set_shader_parameter("street_mask", load("res://assets/district_500/surface_mask.png"))
	var textures := {
		"asphalt": "asphalt_02_diff_1k.jpg",
		"asphalt_normal": "asphalt_02_nor_gl_1k.jpg",
		"asphalt_rough": "asphalt_02_rough_1k.png",
		"paving": "stone_floor_diff_2k.jpg",
		"paving_normal": "stone_floor_nor_gl_2k.jpg",
		"soil": "brown_mud_leaves_01_diff_2k.jpg",
		"aggregate": "leaf_scattered_gravel_diff_2k.jpg",
	}
	for key: String in textures:
		ground.set_shader_parameter(key, load("res://assets/chongqing_district_" + textures[key]))
	for tile: MeshInstance3D in district.find_children("COL_Outer500_Surface_*", "MeshInstance3D", true, false):
		tile.material_override = ground
	var local_frame := city.find_child("LocalCityFrame", true, false) as Node3D
	if local_frame:
		local_frame.hide()
	for bank_name in ["R22_Bank_Outer", "R22_Bank_Relief"]:
		var bank := city.find_child(bank_name, true, false) as MeshInstance3D
		if bank:
			(bank.get_surface_override_material(0) as ShaderMaterial).set_shader_parameter("outer_district_cut", true)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	for plot: Dictionary in layout.plots:
		if plot.has("repair_court"):
			district.set_meta("repair_court",plot.repair_court)
	var cut: Dictionary = layout.get("interior_rail_return", {})
	if not cut.is_empty():
		var old_rail := city.find_child(cut.original,true,false) as MeshInstance3D
		var new_rail := district.find_child(cut.replacement,true,false) as MeshInstance3D
		if old_rail and new_rail:
			for surface in mini(old_rail.mesh.get_surface_count(),new_rail.mesh.get_surface_count()):
				new_rail.set_surface_override_material(surface,old_rail.get_active_material(surface))
			old_rail.hide()
	for item: MeshInstance3D in district.find_children("Outer500_Household_*","MeshInstance3D",true,false):
		item.visibility_range_end=39.0
		item.lod_bias=1.7
	for mesh: MeshInstance3D in district.find_children("Outer500_CourtDetails_*","MeshInstance3D",true,false):
		mesh.lod_bias=3.0
	for unit: MeshInstance3D in district.find_children("Outer500_Condenser_*","MeshInstance3D",true,false):
		unit.visibility_range_end=55.0
	var edge: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/edge_ground.json"))
	for prefix: String in edge.context_prefixes:
		for mesh: MeshInstance3D in city.find_children(prefix+"*","MeshInstance3D",true,false):
			mesh.global_position.y+=float(edge.context_shift_z)
	var prefixes: Array = layout.get("retired_context_prefixes", [])
	for prior: MeshInstance3D in city.find_children("Context_*","MeshInstance3D",true,false):
		for prefix: String in prefixes:
			if str(prior.name).begins_with(prefix):
				prior.hide()
				break
	var roofs := city.find_child("R21_Rooftop_stairheads",true,false) as MeshInstance3D
	if roofs and not layout.get("retired_roof_positions",[]).is_empty():
		trim_roofs(roofs,layout.retired_roof_positions)
	var trunks := StaticBody3D.new()
	trunks.name = "OuterDistrictTreeTrunks"
	trunks.collision_layer = 1
	trunks.collision_mask = 0
	district.add_child(trunks)
	# Near trees keep the scanned leaves. Beyond the pavement use the same species'
	# four-direction atlas as the existing hillside, grouped into small street cells.
	var distant_trees := []
	var tree_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_r21/layout.json"))
	for plant: MeshInstance3D in district.find_children("Outer500_Plant_*", "MeshInstance3D", true, false):
		plant.lod_bias = 5.0
		plant.visibility_range_end = 38.0
	var court_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/historic_courts.json"))
	var replaced_roots: Array[Vector2]=[]
	for centre: Array in court_data.superseded_outer_roots + guoco_plant_roots:
		replaced_roots.append(Vector2(centre[0],centre[1]))
	var planting: Array=layout.planting
	for index in planting.size():
		var tree: Dictionary=planting[index]
		var name := "Outer500_Plant_%03d"%index
		if name in nanqu_retired_meshes:
			continue
		var p: Array=(relocated if index==36 else tree.east_north_up).duplicate()
		if nanqu_rebased_trees.has(name):
			p[2]=nanqu_rebased_trees[name]
		var centre:=Vector2(p[0],p[1])
		if replaced_roots.any(func(old: Vector2): return old.distance_squared_to(centre)<.01):
			var prior:=district.find_child("Outer500_Plant_%03d"%index,true,false) as MeshInstance3D
			if prior:
				prior.hide()
			continue
		var cylinder := CylinderShape3D.new()
		cylinder.radius = 0.13 * tree.width_scale
		cylinder.height = 1.8 * tree.height_scale
		var shape := CollisionShape3D.new()
		shape.shape = cylinder
		shape.position = Vector3(p[0], p[2] + cylinder.height / 2.0, -p[1])
		trunks.add_child(shape)
		var scan_height := 4.54 if int(tree.species) == 0 else 5.02
		distant_trees.append({"position":[p[0], p[2], -p[1]], "height":scan_height * float(tree.height_scale),
			"kind":tree.species, "yaw":deg_to_rad(tree.rotation_deg), "shade":0.94})
	preload("res://scripts/district_r21.gd").install_canopy(district, distant_trees, tree_data.canopy_pivots, 8.0, 34.0)
	var retire: Array = layout.get("osm_building_ids", []) + xingchen_way
	for way: float in market_ways:
		retire.append(int(way))
	for id: int in retire:
		for prior: Node3D in city.find_children("Context_*%s_*" % id, "MeshInstance3D", true, false):
			prior.hide()
	for place: Dictionary in layout.destinations:
		var sign := Label3D.new()
		var northeast: Array = place.east_north
		var angle: float = place.bearing
		var offset: float = place.front_offset - 2.235
		sign.position = Vector3(northeast[0] - sin(angle) * offset, place.height + 2.38,
			-northeast[1] - cos(angle) * offset)
		sign.rotation.y = angle
		sign.text = place.name
		sign.modulate = Color("#f0e2b9")
		sign.outline_modulate = Color("#2d2822")
		sign.outline_size = 12
		sign.font = load("res://assets/district_500/district_signs.otf")
		sign.font_size = 72
		sign.pixel_size = 0.0051
		sign.no_depth_test = false
		district.add_child(sign)
	for plot: Dictionary in layout.get("plots",[]):
		if plot.has("superseded_by") or plot.plot_id in retired_bridge_plots:
			continue
		for spec: Dictionary in plot.get("trade_signs",[]):
			var lettering:=Label3D.new()
			var yaw: float=plot.bearing
			lettering.text=spec.text
			lettering.font=load("res://assets/district_500/district_signs.otf")
			lettering.font_size=64
			lettering.pixel_size=.00325
			lettering.modulate=Color("#e8dec4")
			lettering.outline_size=3
			lettering.rotation.y=yaw
			lettering.position=Vector3(plot.east_north[0]+cos(yaw)*spec.u-sin(yaw)*spec.v,plot.height+spec.h,
				-plot.east_north[1]-sin(yaw)*spec.u-cos(yaw)*spec.v)
			district.add_child(lettering)
		if plot.name=="照相巷便民市场" or plot.name=="南区路车棚修理铺":
			place_worker(district,plot)
		if not plot.has("court"):
			continue
		var court: Dictionary=plot.court
		var label:=Label3D.new()
		var u: float=court.room_u+.83*court.stair_side
		var v: float=court.room_v-1.05
		var a: float=plot.bearing
		label.text="201"
		label.font_size=48
		label.pixel_size=.0022
		label.modulate=Color("#e7dcc7")
		label.outline_modulate=Color("#27433d")
		label.outline_size=9
		label.rotation.y=a
		label.position=Vector3(plot.east_north[0]+cos(a)*u-sin(a)*v,plot.height+court.upper_m+1.76,
			-plot.east_north[1]-sin(a)*u-cos(a)*v)
		district.add_child(label)
	return {"bounds_east_north_m": layout.bounds_east_north_m,
		"glb_sha256": FileAccess.get_sha256(MODEL), "riverside_sha256": FileAccess.get_sha256(RIVERSIDE),
		"match_factory_sha256": FileAccess.get_sha256(MATCH_FACTORY),
		"matix_streets_sha256": FileAccess.get_sha256(MATIX_STREETS),
		"zhongxing_wall_sha256": FileAccess.get_sha256(ZHONGXING_WALL),
		"west_court_sha256": FileAccess.get_sha256(WEST_COURT),
		"west_ramp_sha256": FileAccess.get_sha256(WEST_RAMP),
		"guoco_sha256": FileAccess.get_sha256(GUOCO),
		"houci_77_sha256": FileAccess.get_sha256(HOUCI) if houci_active else "",
		"panda_15_17_sha256": FileAccess.get_sha256(PANDA) if panda_active else "",
		"zhongxing_18_21_sha256": FileAccess.get_sha256(ZHONGXING_BRIDGE) if bridge_margins_active else "",
		"houci_14_16_sha256": FileAccess.get_sha256(HOUCI_CONNECTORS) if connectors_active else "",
		"fenghuangtai_11_sha256": FileAccess.get_sha256(FENGHUANGTAI_11) if lower_junction_active else "",
		"wilderness_50_sha256": FileAccess.get_sha256(WILDERNESS_50) if wilderness_active else "",
		"wilderness_50_finish_sha256": FileAccess.get_sha256(WILDERNESS_FINISH) if wilderness_finish_active else "",
		"north_38_40_41_sha256": FileAccess.get_sha256(NORTH_EDGES) if north_active else "",
		"liangtingzi_45_46_sha256": FileAccess.get_sha256(LIANGTINGZI) if liangtingzi_active else "",
		"mati_34_35_sha256": FileAccess.get_sha256(MATI34_35) if mati34_active else "",
		"zhongxing_public_edges_sha256": FileAccess.get_sha256(ZHONGXING_PUBLIC_EDGES) if zhongxing_public_active else "",
		"nanqu_04_06_51_sha256": FileAccess.get_sha256(NANQU) if nanqu_active else "",
		"changbin_55_sha256": FileAccess.get_sha256(CHANGBIN_55) if changbin55_active else "",
		"public_edges_sha256": FileAccess.get_sha256(PUBLIC_EDGES),
		"xingchen_sha256": FileAccess.get_sha256(XINGCHEN),
		"pavilion_62_sha256": FileAccess.get_sha256(PAVILION_62),
		"collectibles_market_sha256": FileAccess.get_sha256(COLLECTIBLES),
		"market_stall_row_sha256": FileAccess.get_sha256(MARKET_STALL_ROW),
		"park_plot57_sha256": FileAccess.get_sha256(PARK_PLOT_57),
		"bridge_park_sha256": FileAccess.get_sha256(BRIDGE_PARK),
		"park_plot59_sha256": FileAccess.get_sha256(PARK_PLOT_59),
		"park_plot61_sha256": FileAccess.get_sha256(PARK_PLOT_61),
		"park_edge_finish_sha256": FileAccess.get_sha256(PARK_EDGE_FINISH),
		"changbin_bend_sha256": FileAccess.get_sha256(CHANGBIN_BEND),
		"raijiapo_east_sha256": FileAccess.get_sha256(RAIJIAPO_EAST),
		"binjiang_sha256": FileAccess.get_sha256(BINJIANG),
		"retired_internal_context": local_frame != null, "osm_building_ids": retire}


static func add_public_edge_trees(district: Node3D, layer: Node, trees: Array) -> void:
	for row: Dictionary in trees:
		var donor := district.find_child(row.donor,true,false) as MeshInstance3D
		assert(donor,row.donor)
		var tree := donor.duplicate() as MeshInstance3D
		tree.name = row.name
		tree.position = enu(row.enu)
		tree.scale *= float(row.scale)
		tree.rotation.y += float(row.yaw)
		layer.add_child(tree)


static func install_street_group(district: Node3D, model_path: String, plan_path: String, group_name: String) -> void:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	var layer := (load(model_path) as PackedScene).instantiate() as Node3D
	layer.name = group_name
	var textures: Dictionary = plan.get("surface_textures", {})
	if not textures.is_empty():
		for part: MeshInstance3D in layer.find_children("*", "MeshInstance3D", true, false):
			for index in part.mesh.get_surface_count():
				var finish := part.mesh.surface_get_material(index) as BaseMaterial3D
				if finish != null and textures.has(finish.resource_name):
					finish.albedo_texture = load(textures[finish.resource_name]) as Texture2D
	for mesh_name: String in plan.replacement_meshes:
		var original := district.find_child(mesh_name, true, false) as MeshInstance3D
		var updated := layer.find_child(mesh_name, true, false) as MeshInstance3D
		assert(original and updated, mesh_name)
		var slots: Dictionary = plan.get("borrowed_materials",{}).get(mesh_name,{})
		if not slots.is_empty():
			restore_street_materials(original,updated,slots)
		original.mesh = updated.mesh
		updated.free()
	for mesh_name: String in plan.retired_objects:
		var old := district.find_child(mesh_name, true, false)
		assert(old, mesh_name)
		old.free()
	district.add_child(layer)

static func restore_street_materials(original: MeshInstance3D, updated: MeshInstance3D, slots: Dictionary) -> void:
	var materials := {}
	for i in original.mesh.get_surface_count():
		var material := original.mesh.surface_get_material(i)
		if material:
			materials[material.resource_name] = material
	for i in updated.mesh.get_surface_count():
		var material := updated.mesh.surface_get_material(i)
		if material and material.resource_name in slots:
			var donor: String = slots[material.resource_name]
			assert(materials.has(donor), "%s %s" % [original.name, donor])
			updated.mesh.surface_set_material(i, materials[donor])


static func place_east_tree(district: Node3D, spec: Dictionary) -> void:
	var donor := district.find_child(spec.donor,true,false) as MeshInstance3D
	var plant := donor.duplicate() as MeshInstance3D
	plant.name=spec.name
	plant.position=enu(spec.enu)
	plant.scale*=.89
	plant.rotation.y+=.83
	district.get_node("RaijiapoEastBend").add_child(plant)

static func load_binjiang_plan() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(BINJIANG_SITE))

static func hide_replaced_binjiang_facades(city: Node3D, names: Array) -> void:
	for mesh_name: String in names:
		var former := city.find_child(mesh_name,true,false) as MeshInstance3D
		if former:
			former.hide()

static func binjiang_plot() -> String:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--binjiang-plot="):
			return arg.trim_prefix("--binjiang-plot=")
	return ""


static func finish_park_trees(district: Node3D) -> void:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PARK_EDGE_FINISH_SITE))
	for label: String in plan.tree_local_scale:
		var tree := district.find_child(label,true,false) as MeshInstance3D
		var scale: Array = plan.tree_local_scale[label]
		tree.scale *= Vector3(scale[0],scale[2],scale[1])
	var park := district.get_node("RiversideParkEdgeFinish")
	for entry: Dictionary in plan.planted_trees:
		var donor := district.find_child(entry.donor,true,false) as MeshInstance3D
		var tree := donor.duplicate() as MeshInstance3D
		tree.name = entry.name
		tree.position = enu(entry.east_north_up)
		tree.rotation.y += float(entry.yaw_offset_rad)
		tree.scale *= float(entry.scale)
		park.add_child(tree)

static func add_collectibles_details(district: Node3D, plan: Dictionary) -> void:
	var sign := Label3D.new()
	sign.name = "ZhongxingMarketName"
	sign.text = "中兴路收藏品交易市场"
	sign.font = load("res://assets/district_500/market_signs.otf")
	sign.font_size = 114
	sign.pixel_size = .011
	sign.modulate = Color("#c35143")
	sign.outline_size = 1
	sign.outline_modulate = Color("#411c16")
	sign.rotation.y = -PI / 2.0
	sign.position = enu(plan.sign_east_north_up)
	district.add_child(sign)
	for enu_position: Array in [[227.0,193.15,56.22],[231.0,189.87,56.05],[230.0,197.56,56.12]]:
		var light := OmniLight3D.new()
		light.position = enu(enu_position)
		light.light_color = Color("#edeee1")
		light.light_energy = .91
		light.omni_range = 6.2
		district.add_child(light)

static func place_worker(district: Node3D,p: Dictionary) -> void:
	var market: bool=p.name=="照相巷便民市场"
	var model: Node3D=(load("res://assets/block_r23/neighbor.glb" if market else "res://assets/block_r23/commuter.glb") as PackedScene).instantiate()
	model.name="OuterMarketSeller" if market else "OuterRepairWorker"
	district.add_child(model)
	var a: float=p.bearing
	var u:=2.90 if market else 2.13
	var v: float=-p.depth/2.0+4.65 if market else -.45
	model.position=Vector3(p.east_north[0]+cos(a)*u-sin(a)*v,p.height+.041,-p.east_north[1]-sin(a)*u-cos(a)*v)
	model.rotation.y=a+(.11 if market else PI*.55)
	var player:=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var library: AnimationLibrary=load("res://assets/frontage_r24/stall_clips.res" if market else "res://assets/courtyard_r24/wait_clips.res")
	var clip: StringName=&"street/watch_street" if market else &"street/commuter"
	player.add_animation_library("street",library)
	player.play(clip)
	player.seek(.57,true)
	var enabler:=VisibleOnScreenEnabler3D.new()
	model.add_child(enabler)
	enabler.aabb=AABB(Vector3(-.65,0,-.65),Vector3(1.3,2.15,1.3))
	enabler.enable_node_path=enabler.get_path_to(player)
	for part: MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
		part.visibility_range_end=45.

static func trim_roofs(node: MeshInstance3D, anchors: Array) -> void:
	var original := node.mesh
	var retained := ArrayMesh.new()
	for surface in original.get_surface_count():
		var arrays := original.surface_get_arrays(surface)
		var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		if indices.is_empty():
			indices=PackedInt32Array(range(positions.size()))
		var keep := PackedInt32Array()
		for i in range(0,indices.size(),3):
			var center := node.to_global((positions[indices[i]]+positions[indices[i+1]]+positions[indices[i+2]])/3.0)
			var removed := false
			for a: Array in anchors:
				if absf(center.x-a[0])<2.35 and absf(center.z-a[2])<1.65 and center.y>a[1]-.10 and center.y<a[1]+4.65:
					removed=true
					break
			if not removed:
				keep.append_array(indices.slice(i,i+3))
		if not keep.is_empty():
			arrays[Mesh.ARRAY_INDEX]=keep
			retained.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
			retained.surface_set_material(retained.get_surface_count()-1,node.get_active_material(surface))
	node.mesh=retained

static func enu(p: Array) -> Vector3:
	return Vector3(p[0],p[2],-float(p[1]))

static func zhongxing_public_view() -> String:
	for id in ["14","16","18"]:
		if ("--zhongxing-public=" + id) in OS.get_cmdline_user_args():
			return id
	return ""

static func start_exploration(scene: Node3D) -> void:
	var collision := preload("res://scripts/build_collisions.gd")
	var bike := scene.gameplay.scooter as CharacterBody3D
	var road := collision.raycast_ground(scene, Vector3(102.0, 21.0, 42.1), 10.0)
	var shoulder := collision.raycast_ground(scene, Vector3(101.1, 21.0, 41.1), 10.0)
	if road.is_empty() or shoulder.is_empty():
		push_error("The 500 m exploration entry lost its road support")
		return
	bike.global_position = road.position + Vector3.UP * 0.035
	bike.safe_park_position = bike.global_position
	bike.rotation.y = -0.87
	scene.explorer.set_walk_origin(shoulder.position + Vector3.UP * 0.035, bike.global_position + Vector3.UP)
	if "--repair-court" in OS.get_cmdline_user_args():
		var site: Dictionary=scene.get_node("City/OuterDistrict500").get_meta("repair_court")
		bike.global_position=enu(site.bike)
		bike.safe_park_position=bike.global_position
		bike.tyre_pressure=1.15
		scene.explorer.set_walk_origin(enu(site.street)+Vector3.UP*.035,enu(site.porch)+Vector3.UP)
	elif "--shancheng" in OS.get_cmdline_user_args():
		var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/shancheng_lane.json"))
		var a: Array=layout.public_stops[0].approach
		var b: Array=layout.public_stops[0].target
		scene.explorer.set_walk_origin(Vector3(a[0],a[2],-a[1]),Vector3(b[0],b[1],b[2]))
	elif "--zhongxing-collectibles" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(COLLECTIBLES_SITE))
		var point: Array = plan.route_east_north[0]
		var street := collision.raycast_ground(scene, Vector3(point[0], 52.1, -point[1]), 8.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035,
				enu(plan.street_eye_target_east_north_up))
	elif "--houci-77" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(HOUCI_SITE))
		var point: Array = plan.walk.stations[0]
		var street := collision.raycast_ground(scene, Vector3(point[0], plan.walk.start_ray_y, -point[1]), 3.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(plan.walk.start_aim_enu))
	elif "--zhongxing-bridge-21" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ZHONGXING_BRIDGE_SITE))
		var origin := enu(plan.lower_walk_21[0])
		var street := collision.raycast_ground(scene, origin + Vector3.UP * 1.1, 3.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(plan.lower_walk_21[1]))
	elif "--nanqu-riverwalk" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(NANQU_SITE))
		var points: Array = plan.public_walk
		var parent := "--qa-without-nanqu-04-06-51" in OS.get_cmdline_user_args()
		var from := enu(points[0]) + Vector3.UP * (8.0 if parent else 0.8)
		var street := collision.raycast_ground(scene, from, 12.0 if parent else 2.4)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(points[1]))
		var parking := enu(plan.bike_path[1])
		var vehicle := collision.raycast_ground(scene, parking + Vector3.UP * (8.0 if parent else 0.8), 12.0 if parent else 2.4)
		if not vehicle.is_empty():
			bike.global_position = vehicle.position + Vector3.UP * .035
			bike.safe_park_position = bike.global_position
	elif "--wilderness-50" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WILDERNESS_50_SITE))
		var points: Array = plan.public_route
		var street := collision.raycast_ground(scene, enu(points[0]) + Vector3.UP * .8, 2.4)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(points[1]))
	elif "--fenghuangtai-11" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FENGHUANGTAI_11_SITE))
		var points: Array = plan.site_walk
		var street := collision.raycast_ground(scene, enu(points[0]) + Vector3.UP * .9, 3.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(points[1]))
	elif not zhongxing_public_view().is_empty():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(HOUCI_CONNECTORS_SITE))
		var points: Array = plan.public_walks[zhongxing_public_view()]
		var origin := enu(points[0])
		var street := collision.raycast_ground(scene, origin + Vector3.UP * .9, 3.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(points[1]))
	elif "--panda-15" in OS.get_cmdline_user_args() or "--panda-17" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PANDA_SITE))
		var site: Dictionary = plan.route["17" if "--panda-17" in OS.get_cmdline_user_args() else "15"]
		var point: Array = site.stations[0]
		var street := collision.raycast_ground(scene, Vector3(point[0], site.start_ray_y, -point[1]), 3.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(site.street_focus))
	elif binjiang_plot() in ["70","71","72","73"]:
		var route: Dictionary = load_binjiang_plan().public_routes[binjiang_plot()]
		var start: Array = route.stations[0]
		var next: Array = route.stations[1]
		var street := collision.raycast_ground(scene, Vector3(start[0],route.start_ground_m+.85,-start[1]),2.4)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position+Vector3.UP*.035,Vector3(next[0],street.position.y,-next[1]))
	elif "--raijiapo-east" in OS.get_cmdline_user_args():
		var route: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RAIJIAPO_EAST_SITE)).walk
		var origin: Array = route.stations[0]
		var aim: Array = route.stations[1]
		var street := collision.raycast_ground(scene, Vector3(origin[0], route.start_ray_m, -origin[1]), 6.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, Vector3(aim[0], street.position.y, -aim[1]))
	elif "--changbin-bend" in OS.get_cmdline_user_args() or "--changbin-park-edge" in OS.get_cmdline_user_args():
		var routes: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CHANGBIN_BEND_SITE)).routes
		var route: Dictionary = routes.bend if "--changbin-bend" in OS.get_cmdline_user_args() else routes.park
		var start: Array = route.stations[0]
		var street := collision.raycast_ground(scene, Vector3(start[0], route.start_ray_height_m, -start[1]), 6.0)
		if not street.is_empty():
			var aim: Array = route.stations[1]
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, Vector3(aim[0], street.position.y, -aim[1]))
	elif "--park-59" in OS.get_cmdline_user_args() or "--park-61" in OS.get_cmdline_user_args():
		var site := PARK_PLOT_61_SITE if "--park-61" in OS.get_cmdline_user_args() else PARK_PLOT_59_SITE
		var park: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(site))
		var start: Array = park.route_east_north[0]
		var ground := collision.raycast_ground(scene,Vector3(start[0],6.0,-start[1]),12.0)
		if not ground.is_empty():
			var next: Array = park.route_east_north[1]
			scene.explorer.set_walk_origin(ground.position+Vector3.UP*.035,Vector3(next[0],ground.position.y,-next[1]))
	elif not north_edge_mode().is_empty():
		var plot := north_edge_mode()
		var paths := {"34":MATI34_35_SITE,"35":MATI34_35_SITE,"45":LIANGTINGZI_SITE,"46":LIANGTINGZI_SITE}
		for id: String in ["10","12","13","22"]:
			paths[id]=ZHONGXING_PUBLIC_EDGES_SITE
		var path: String = paths.get(plot,NORTH_EDGES_SITE)
		var north: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
		var rows: Array=north.walks[plot]
		var street := collision.raycast_ground(scene,enu(rows[0])+Vector3.UP*.8,2.4)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position+Vector3.UP*.035,enu(rows[1]))
	elif "--changbin-55-park" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CHANGBIN_55_SITE))
		var rows: Array = plan.walk
		var street := collision.raycast_ground(scene, enu(rows[-1]) + Vector3.UP * .8, 2.4)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, enu(rows[-2]))
	elif "--west-court" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WEST_COURT_SITE))
		var ramp: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WEST_RAMP_SITE))
		var street_access := "--west-street-court" in OS.get_cmdline_user_args()
		var start: Array = ramp.playground.street_access.route_east_north[0] if street_access else ramp.street_route_east_north[0]
		var focus: Array = ramp.playground.street_access.street_focus_east_north_up if street_access else ramp.street_focus_east_north_up
		var join: Array = plan.walk_plan.ramp[0]
		var trail := collision.raycast_ground(scene, Vector3(start[0], 4.5 if street_access else -.9, -start[1]), 17.)
		var park := collision.raycast_ground(scene, Vector3(join[0] + 4.5, -4., -join[1] + 2.), 10.)
		if not trail.is_empty() and not park.is_empty():
			bike.global_position = park.position + Vector3.UP * .035
			bike.safe_park_position = bike.global_position
			bike.rotation.y = -1.72
			scene.explorer.set_walk_origin(trail.position + Vector3.UP * .035,enu(focus))
	elif "--riverside" in OS.get_cmdline_user_args():
		var park := collision.raycast_ground(scene, Vector3(-205.0, -12.0, 210.0), 6.0)
		if not park.is_empty():
			scene.explorer.set_walk_origin(park.position + Vector3.UP * 0.035, Vector3(-191.0, -13.5, 214.0))
	elif "--match-factory" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATCH_FACTORY_SITE))
		var point: Array = plan.walks_east_north.lower_frontage[0]
		var factory := collision.raycast_ground(scene, Vector3(point[0], 20.0, -point[1]), 15.0)
		if not factory.is_empty():
			scene.explorer.set_walk_origin(factory.position + Vector3.UP * .035, Vector3(230, 14, 119))
	elif "--matix-streets" in OS.get_cmdline_user_args():
		var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MATIX_SITE))
		var point: Array = plan.spawn_east_north
		var street := collision.raycast_ground(scene, Vector3(point[0], 48.0, -point[1]), 16.0)
		if not street.is_empty():
			scene.explorer.set_walk_origin(street.position + Vector3.UP * .035, Vector3(-64, 42, -145))
	if "--outer-market" in OS.get_cmdline_user_args():
		var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
		for i in layout.plots.size():
			var p: Dictionary=layout.plots[i]
			if p.name!="照相巷便民市场": continue
			var a: float=p.bearing
			var v: float=-p.depth/2.0-1.92
			var u: float=-p.width*.27
			var landing:=Vector3(p.east_north[0]+cos(a)*u-sin(a)*v,p.height+.075,
				-p.east_north[1]-sin(a)*u-cos(a)*v)
			var focus:=Vector3(p.east_north[0],p.height+1.14,-p.east_north[1])
			scene.explorer.set_walk_origin(landing,focus)
			for lane: Dictionary in layout.lanes:
				if lane.type=="street" and lane.plots[0]==i:
					var xy: Array=lane.points[1]
					var ground:=collision.raycast_ground(scene,Vector3(xy[0],p.height+4.0,-xy[1]),22.0)
					if not ground.is_empty():
						bike.global_position=ground.position+Vector3.UP*.035
						bike.safe_park_position=bike.global_position
					break
			break
