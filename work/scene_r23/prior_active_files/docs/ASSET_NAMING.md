# 资产命名

R22 分为 roofs_r22/roofs_and_breakfast.glb 和 river_r22/river_context.glb，均有对应独立 Blender 源及 layout.json。远景车辆父节点用 TransitActor 加字母。Godot 场景导入器会把 Vehicle 标记解释成物理车辆，原名会丢失。按导入后节点名检查。

R21 使用 assets/district_r21。terraces.glb 是建筑增量，layout.json 保存基础、屋面和种植落位，wall_fields.json 索引核心建筑的窗下雨痕。完整 Blender 城市源和独立环境图层分别命名为 chongqing_district.blend 与 district_environment.blend。相机名沿用 R20，复拍时按画面清单中的相机位置、朝向、视角及状态比对。

R20 上巷场景位于 assets/lane_r20。upper_lane.glb 是增量场景，meter_lods.glb 是按原柜体位置生成的渲染模型。树池居民的模型、落位和许可在 assets/characters/court_resident，游戏交互使用稳定标识 residents.court.neighbor。两个可坐位置使用各自的 residents.bench 标识，起身由玩家的就座状态处理。
R19保持基础城市GLB的旧名称/清单；新增 `assets/street_r19/street_life.glb`、`manifest.json`、`PROVENANCE.json`。R19_为可见细节，COL_R19_为实体挡边，COLH_R19_为隐形物理代理。旧网格只按明确的替换清单隐藏，不能删掉恢复来源。组合版本记录在 `assets/scene_composition_r19.json`。

保留 R15 既有名称，防止碰撞筛选失效。新增修正使用 COL_R16_RoofSeal_<building>、COL_R16_DryingRack_<seed>。COL_ 表示真实碰撞几何，COLH_ 为必要的隐藏碰撞面，禁止为掩盖视觉缺陷增加碰撞墙。

交互使用稳定 ID：vehicle.scooter.99、shop.noodle、delivery.home。显示文字与 ID 分离。文件使用小写英文与下划线，版本写入清单。不得以文件修改时间推断版本。

R17 住宅门铃 ID 为 doorbell.<building_id>.<entrance_index>。R17_Entry_<building>_<index> 是私人门厅细节，R17_Meter_Details 为独立电表细节批次。既有公共路线 COL_Walk_<route> 名称保留，以免丢失碰撞。角色在 assets/characters/shopkeeper_r17.glb，自带来源 JSON 和 CC0 文本；骨骼动画 idle、serve。取餐袋由 takeaway_bag.gd 原创几何构建。

所有交付必须保留 source / scene / exported asset 的对应关系；geometry_repairs_r16.json 记录修正，scene_manifest.json 记录当前版本，旧测试放在明确标注的历史目录。

R18 店主为 assets/characters/shopkeeper_r18.glb，58骨骼，idle/serve/greet；其脚部导入配置与来源文件一并保留。年轻骑手为 assets/characters/rider_r18.glb，源在 work/characters/rider_r18_trial/rider_authoring.blend，动作 ride_idle/ride_steer/ride_support；来自 Rocketbox 的 Bip01 骨骼名保留，避免接触与表情映射错位。运行许可 ROCKETBOX_MIT_LICENSE.txt 与 rider_r18_provenance.json。

可动电瓶车为 assets/vehicles/scooter_r18.glb，源 scooter_articulated.blend；稳定节点 WheelRear / WheelFront / Steering / Kickstand，通过 scooter_visual.gd 使用。城市里六辆原始静态车名称继续保留；交互 ID vehicle.scooter.99 不变。
