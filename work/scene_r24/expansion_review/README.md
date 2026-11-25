# 500 米试作的 Windows 原生对照

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
