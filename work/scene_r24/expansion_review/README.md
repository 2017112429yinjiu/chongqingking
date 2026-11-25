# 500 米试作 · 街面与实机复核

[Windows 直接试玩东侧街口](../../试玩500米城区.cmd) · [正常首日入口](../../打开重庆街区.cmd) · [七个同机位的扩建前后对照](windows/fixed-comparison.jpg) · [东侧实骑短片](windows/east-ride.mp4)

总范围为东西、南北各 500 米。原 200 米核心保留在中心，向四边各扩约 150 米。走出东侧街口可骑车上坡到照相巷便民市场，另有南区路修理铺和江岸茶摊。东侧试玩从自有电瓶车旁出发，按 E 上车，W 前进，A、D 转向，空格刹车，停稳后按 P，再按 E 下车。正常首日仍从报到开始。

## 拍到的问题和修订

- 东侧斜向接头的车道中央原先露出土色。按旧车道的走向平移实测横断面，只在该边界外侧接合，延续旧沥青的采样比例、法线和颗粒方向。[首次原生画面](rejected/east_dirt_in_carriageway.png) · [相同位置修订后](windows/fixed/east.png)
- 从北口仰视，原 R21 的屋顶楼梯间在替换住宅上方悬空。用注册画面的三个像素追到旧屋顶组合网格，随后按三个供体的历史标高重建相应屋面。重开整城后，从附件基座向下量到实际屋面，三处高差均小于 1 毫米。[空中楼梯间](rejected/north_detached_stairhead.png) · [像素命中](rejected/pixel_hits.json) · [北口复拍](windows/fixed/north.png) · [屋面读数](windows/blender/combined_source.json)
- 外圈 306 处树根使用两种项目内的扫描树，邻街保留立体树干、枝叶和贴图，远处复用原项目的多向树冠图。第一次简化把树叶削得过稀，已保留这次截图。新增用地内的原远景植被由相同位置的近、远两档新植被接替。[过度简化的尝试](rejected/north_sparse_leaves.png) · [来源、作者、CC0 许可与输入哈希](plant_sources.json)
- 市场门前通过两道梯段和共用台地衔接。三个新地点分别用原玩家控制器从一道入口上行、穿过门前、从另一道下行，再按原路返回，共走 156.60 米。[市场近景](windows/streets/east_market_landing.png) · [六次连续步行](windows/play/destinations.json)

## 运行范围

Windows 使用 Godot 4.6.3 Forward+ 和 Blender 4.3.2。7 处路口横断面有 2,275/2,275 个命中，四向各有一个距中心 249 米的新区地表命中。五条代表路线各跑双向步行和骑行，20/20 段通过，累计 2,903.43 米。十段骑行均完成上车、停车和下车；每段只在起始就位。[新旧路接头](windows/terrain/sections.json) · [逐段轨迹](windows/play/routes.json) · [试玩入口按键验证](windows/play/explore.json)

10 米网格中，原 200 米范围内部的每一处重叠碰撞面、标高、法线均与基线匹配。区外划作陆地的 2,135 点中有 2,134 点命中，余下的点在西南江岸，距 OSM 岸线约 0.23 米，处于两米岸线网格的取舍范围。另有两个划作水面的采样位置命中岸边几何。核对覆盖时已区分水陆；建筑屋顶和桥面的射线命中不能代替街面通行。[逐点对照](windows/terrain/comparison.json)

本轮门面主要供街面探索，外圈专属配送单和室内尚未制作。部分人行道与土坡仍有较硬的材料边界，临街细节有待玩家在行进中审看。[南侧桥下回看](windows/streets/south_back.png) · [向东出旧区](windows/streets/east_main_out.png) · [区域总览](windows/streets/overview.png)

## 可编辑源和证据

使用 [新区 Blender 源](../district_500/outer_district.blend) 单独编辑，或用 [组合脚本](../district_500/compose.py) 从 25b 的整城源生成 `city_and_outer.local.blend`。该组合相对链接新区及原三个人物库，重开时已确认 13 张外部图片都位于独立检出。可碰撞地表有 84 块，东西和南北各跨 500 米。[Blender 地表范围](windows/blender/blender_footprint.json) · [重开验证](windows/blender/combined_source.json)

原始云端候选为 `e99e544f`。[云端原始报告](../district_500/REPORT.md) 与本目录的硬件证据对应不同提交。视频由 Windows 的 28 张连续原生帧编码，间隔 9 个 60 Hz 物理步，每秒约 6.67 张，片长 4.2 秒。[原始序列](windows/motion)

## 原版基线与复拍命令

基线为 R24 构建 25b。Git 检出为 `0253cada1833dc66fa6a93f12e6af373451e99a4`，游戏基线为 `ce1841b079b78c1f876bfa0da3b8b6a404ac9532`。固定版本 Godot 4.6.3，从实际 `first_shift.tscn` 启动。桌面测量在独立检出内完成。

[原生截图及原始读数](baseline) · [固定机位](fixed_views.gd) · [碰撞射线](edge_profiles.gd)

- 七张原生图覆盖报到街区的服务站、四个朝外的旧路口、斜视总览和俯视。固定视图隐藏内部定位用的 `LocalCityFrame`。旧版南口的画面在上缘能看到上方路面或桥底。两次对照应保留遮挡。
- 旧核心四边各布 101 站，沿边间隔 2 米。每站量距中心 99.65、100.35、108、150、200、245 米处的碰撞。旧区内侧 404/404 点、距中心 245 米处 0/404 点有碰撞。射线在碰到单个碰撞体后排除该体、再查重叠物，屋顶和桥梁仍须按物件名区分。
- 另在总平面量 51 × 51 个点，最外圈略向内收 0.1 米。处在 200 米范围之外的 2160 点中，原版只有 11 点命中任一实体。这个读数用来对照新地面覆盖，实际通行另用步行与骑行检验。
- 三个常用旧街区视角各取 150 帧。Windows 窗口为 1152 × 648，有效视口为 692 × 389。RTX 4070 Laptop GPU 在原版测试期间的一次外部采样为 P8、210 MHz。见 [逐视角帧时](baseline/timing.json)。动态画面与系统功耗状态会影响读数。

用固定版编辑器完成导入后，在仓库根目录运行以下命令。每次使用新的目录名，输出位于 `.cloud-dev/desktop-500`。

```powershell
work/scene_r24/expansion_review/capture.ps1 -Run sample_cameras
work/scene_r24/expansion_review/capture.ps1 -Run sample_terrain -Sections
```
