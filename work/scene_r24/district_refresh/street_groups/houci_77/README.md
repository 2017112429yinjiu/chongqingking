# 厚慈街 77 号公开街面

旧试作住宅的旋转足迹为 19.95 × 9.32 米，地块中心 E208.619 / N−27.939。用项目 `734116601` 控制点校准开放地图和北向影像，厚慈街 `1306489251` 穿过旧轮廓 9.500 米，中心距道路 6.031 米。旧轮廓约 69.93 平方米落在弯内国浩宗地 `1374780312`，宗地线与建筑轮廓分开登记。最近已登记国浩塔楼为 T1 `1374780314`，距旧中心 23.91 米。旁边的南区路匝道 `59146775` 为独立的上层桥，距旧中心 40.31 米。 [开放地图坐标、原图机位与出处](field-registration.json)

区管委会 2023 年记录地面厚慈街已基本建成并办理移交。2016 年最近的街景仍见旧围墙和拆改，2023 年从南区路桥侧拍摄的同址画面可辨桥栏、下层地面和两栋国浩塔，弯口局部仍有施工遮挡。两期有记录的 Wayback 及当前正射同样显示旧楼足迹与地面弯道和内侧开敞地重叠，南侧是塔楼外的浅色硬铺。95 号修缮后的砖券、方孔墙、路缘和塔楼关系可看 2026 年近照，登记点约在本站东侧 127 米，同街不同址。77 号弯口路缘细部、地块内的通行权界、精确铺装分格和真实标高仍待现场核实。 [区管委会](https://www.cqyz.gov.cn/bm_229/lswhjqgwh/zwxx_97154/dt/202307/t20230712_12145003.html) · [2016 年近机位](https://mapsv0.bdimg.com/?qt=pr3d&panoid=09029200011610041054549687G&heading=341&pitch=0&fovy=84&width=840&height=525) · [2023 年桥侧机位](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515143227054AU&heading=148&pitch=0&fovy=84&width=840&height=525) · [95 号修缮图](https://www.cqnews.net/web/content_1503449271585439744.html)

按开放道路节点做低街弯面、两侧窄路缘和灰色人行带。内侧保留开敞绿地，塔基一侧用浅石板承接既有坡面与裙房外沿。2024 年 T2 交付实景的塔基浅灰硬铺用于比对色泽和尺度。沥青、灰石和草复用滨江已制作的米级底图，浅灰路缘使用现有许可混凝土。6.80 米车面、两侧 2.14 / 3.05 米步行带与约 0.10 米路缘高为游戏尺寸，车面从实际游戏碰撞面采样，路口沿当前地形收坡。已测一处 T1 基座旁的室外地表比 77 转身点高 0.93 米。已经登记的 74–76 塔楼及公共裙房通道直接使用原源。旧 77 试作住宅、两个外机、旧梯、柜箱、开放房间与厕所所依附的碰撞随 77 撤下。首版游戏返图发现的车道内旧灯移至弯内绿带，人行带净宽沿用原设计。 [旧面指纹](ownership.json) · [塔基实景](https://www.cqnews.net/1/detail/1298300562114367488/web/content_1298300562114367488.html) · [材质与开源来源](../../../district_500/README.md) · [游戏高程](evidence/foot-and-road-height.json)

## 复开、导入与访问

从仓库根目录用 Blender 4.3.2 生成轻量链接组合，读取已校验的既有素材。用 Godot 4.6.3 导入和实走正常场景。通行 QA 反向在同一玩家原地转身。加 `--qa-without-houci-77` 可用同一条路线和同一组镜头复现父版。

```sh
site=work/scene_r24/district_refresh/street_groups/houci_77
game=work/project/chongqing_godot_v05
CQ_HOUCI_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_houci.local.blend --python-exit-code 1 --python "$site/build.py" -- "$site"
mv "$site/houci-77.glb" "$site/houci-77.json" "$game/assets/district_500/"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b "$site/houci-77.blend" --python-exit-code 1 --python "$site/check_source.py"
godot --headless --path "$game" --import
mkdir -p /tmp/houci-77-walk
CQ_QA_DIR=/tmp/houci-77-walk godot --headless --path "$game" --fixed-fps 60 --script "$PWD/$site/walk.gd" -- --day-one-test --qa-still-frames --explore-500 --houci-77
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --houci-77
```
