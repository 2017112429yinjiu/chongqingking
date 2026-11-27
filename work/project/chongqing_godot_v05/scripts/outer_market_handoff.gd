extends RefCounted
## Optional local delivery on the two existing public counters in Plot 01.

const Job := preload("res://scripts/shancheng_delivery.gd")
const MARKET := {
	"id":"outer_market", "sender":"时令蔬菜摊 · 取件", "receiver":"干货摊 · 交接",
	"pickup":"向摊主领取分装菜品（6元）", "dropoff":"把菜品交到干货摊",
	"ticket":"便民市场 · 菜品托送", "receipt":"便民市场 · 已签收", "reward":6,
	"carrying":"市场托送 · 把菜品送到主厅对侧干货摊",
	"ready":"照相巷便民市场 · 时令蔬菜摊取件",
	"done":"市场主厅已交接 · 6元",
	"collected":"摊主已交件 · 前往主厅干货摊",
	"paid":"主厅已签收 · 配送收入 +6元",
}

static func counter_point(plot: Dictionary, u: float, v: float, height: float) -> Vector3:
	var c := cos(float(plot.bearing))
	var s := sin(float(plot.bearing))
	return Vector3(plot.east_north[0]+c*u-s*v,plot.height+height,-plot.east_north[1]-s*u-c*v)

static func stop(plot: Dictionary, approach_u: float, approach_v: float, u: float, v: float, target_rise := .826) -> Dictionary:
	var a := counter_point(plot,approach_u,approach_v,0.)
	var b := counter_point(plot,u,v,target_rise)
	return {"approach":[a.x,-a.z,a.y],"target":[b.x,b.y,b.z],"parcel_y":plot.height+.76}

static func install(game: Node3D) -> void:
	if not game.owner_scene.find_child("OuterMarketSeller",true,false):
		return
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/district_500/layout.json"))
	var plot: Dictionary = layout.plots.filter(func(row: Dictionary) -> bool: return int(row.plot_id)==1)[0]
	var handoff := Job.new()
	handoff.name = "Plot01MarketHallHandoff"
	game.add_child(handoff)
	game.outer_market_handoff = handoff
	handoff.setup(game,[
		stop(plot,-.08,-1.85,1.42,-1.28),
		stop(plot,-1.53,.62,-3.14,.62,.96),
	],MARKET)
