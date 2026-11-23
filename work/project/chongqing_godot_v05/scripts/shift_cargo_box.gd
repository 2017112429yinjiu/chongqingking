extends RefCounted
var box: Node3D
var hinge: Node3D
func install(vehicle: CharacterBody3D) -> void:
	var original:Node3D = vehicle.articulation.vehicle
	var rubber:MeshInstance3D=original.find_child("Scooter_Body_rubber",true,false)
	var orange:MeshInstance3D=original.find_child("Scooter_Body_plastic_orange",true,false)
	box=preload("res://assets/vehicles/first_shift_box.glb").instantiate()
	original.add_child(box)
	hinge=box.find_child("LidHinge",true,false)
	var fixed:MeshInstance3D=box.find_child("FixedRubber",true,false)
	fixed.material_override=rubber.get_active_material(0)
	orange.hide()
	rubber.hide()

func open(fraction:float) -> void:
	hinge.rotation.x=deg_to_rad(100.)*clampf(fraction,0.,1.)

func lid_edge(side:float) -> Vector3:
	return hinge.to_global(Vector3(side*.257,.033,-.155))

func stored() -> Vector3:
	return box.to_global(Vector3(.05,.868,.58))

func handle_path(start:Vector3,t:float,side:float) -> Vector3:
	var outer:=box.to_global(Vector3(side*.397,1.598,.397))
	var over:=box.to_global(Vector3(.079,1.598,.58))
	var end:=stored()+Vector3.UP*.331
	# Round both corners inside the clearance allowance. Travel along the complete
	# path at one eased speed, without a stop and restart over the rider's head.
	var lip_path:=PackedVector3Array([start])
	for corner:Array in [[start,outer,over],[outer,over,end]]:
		var mid:Vector3=corner[1]
		var entry:=mid+mid.direction_to(corner[0])*.022
		var exit:=mid+mid.direction_to(corner[2])*.022
		for k in 5:
			var u:=k*.25
			lip_path.append(entry.lerp(mid,u).lerp(mid.lerp(exit,u),u))
	lip_path.append(end)
	var length:=0.
	for k in range(1,lip_path.size()):length+=lip_path[k-1].distance_to(lip_path[k])
	var distance:=clampf(t,0.,1.)*length
	for k in range(1,lip_path.size()):
		var span:=lip_path[k-1].distance_to(lip_path[k])
		if distance<=span:return lip_path[k-1].lerp(lip_path[k],distance/maxf(span,.0001))
		distance-=span
	return end
