@tool
extends EditorScenePostImport

func _post_import(scene: Node) -> Object:
	# This project lights the district in relative Godot units. Preserve the
	# physical intensity of the Blender spotlights for physical-unit projects.
	if not ProjectSettings.get_setting("rendering/lights_and_shadows/use_physical_light_units", false):
		for lamp: SpotLight3D in scene.find_children("Story*exhibit*spot*", "SpotLight3D", true, false):
			lamp.light_energy = 1.15
			lamp.shadow_enabled = true
	return scene
