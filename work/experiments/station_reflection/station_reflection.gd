extends RefCounted
## One static cubemap for the small metal workstation; exclude animated people
## and food so a once-updated probe cannot leave a frozen character reflection.
static func attach(game: Node3D) -> void:
	for root: Node3D in [game.shopkeeper,game.bag]:
		for mesh: VisualInstance3D in root.find_children("*","VisualInstance3D",true,false):mesh.layers=2
	var table: Node3D=game.get_node("TakeawayTable")
	for mesh: GeometryInstance3D in table.find_children("*","GeometryInstance3D",true,false):mesh.layers=4
	var probe: ReflectionProbe=ReflectionProbe.new()
	probe.name="PackingStationReflection"
	probe.size=Vector3(6,4,6)
	probe.max_distance=12.0
	probe.box_projection=true
	probe.ambient_mode=ReflectionProbe.AMBIENT_ENVIRONMENT
	probe.enable_shadows=true
	probe.update_mode=ReflectionProbe.UPDATE_ONCE
	probe.cull_mask=1
	probe.reflection_mask=4
	game.add_child(probe)
	probe.global_transform=game.shopkeeper.global_transform
	probe.global_position=game.shopkeeper.to_global(Vector3(.22,1.1,.55))
