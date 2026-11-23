extends SceneTree
func _initialize():
 var group=load("res://assets/river_r22/river_context.glb").instantiate()
 root.add_child(group)
 for child in group.find_children("*","Node3D",true,false):
  if "Vehicle" in str(child.name) or "Traffic" in str(child.name):
   print("ACTOR ",child.name," parent ",child.get_parent().name, " ",child.get_class())
 group.free()
 quit()