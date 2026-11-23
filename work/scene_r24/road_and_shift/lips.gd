extends SceneTree

class TestScooter extends "res://scripts/scooter_controller.gd":
	func has_driver()->bool:return true

func _initialize():call_deferred("run")

func box(parent:Node3D,at:Vector3,size:Vector3) -> void:
	var body:=StaticBody3D.new()
	parent.add_child(body)
	body.position=at
	var volume:=BoxShape3D.new()
	volume.size=size
	var collider:=CollisionShape3D.new()
	collider.shape=volume
	body.add_child(collider)

func run() -> void:
	var results:Array=[]
	for spec in [[.025,0.,1],[.08,0.,1],[.14,.36,1],[.165,0.,1],[.185,.12,1],[.25,0.,1],[.08,.35,-1],[.14,0.,-1],[.36,0.,1],[1.5,.3,1]]:
		var world:=Node3D.new()
		root.add_child(world)
		var h:float=spec[0]
		box(world,Vector3(0,-.5,0),Vector3(16,1,20))
		box(world,Vector3(0,h*.5,-3),Vector3(16,h,6))
		var bike:=TestScooter.new()
		world.add_child(bike)
		bike.position=Vector3(0,.008,1.25)
		bike.rotation.y=spec[1]+(PI if spec[2]<0 else 0.)
		bike.automation=true
		bike.rider_collision.disabled=false
		for i in 12:await physics_frame
		bike.test_throttle=spec[2]
		var peak:=0.
		for i in 152:
			await physics_frame
			peak=maxf(peak,bike.position.y)
			if bike.position.z< -1.05:break
		var crossed:=bike.position.z< -1.
		results.append({"height_m":h,"angle_rad":spec[1],"throttle":spec[2],"crossed":crossed,"pass":crossed==(h<=.20),"max_body_y":peak,"position":str(bike.position)})
		world.queue_free()
		await process_frame
		await physics_frame
	var dir:=preload("res://scripts/qa_context.gd").directory("res://verification_r24/road_shift/lips")
	FileAccess.open(dir.path_join("results.json"),FileAccess.WRITE).store_string(JSON.stringify(results,"\t"))
	print("ROAD_LIPS ",JSON.stringify(results))
	quit(0 if results.all(func(r):return r["pass"]) else 2)
