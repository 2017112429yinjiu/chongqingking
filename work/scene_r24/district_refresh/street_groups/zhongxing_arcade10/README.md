# 中兴路 10 号公共砖廊

父版 `473b41e7329a30388adc9a25bfc53bbb381eb689`。2023-05-15 南侧 42°、北侧 90° 两眼独立取白柱帽，再以南 13°、北 72° 或 137° 验同一构件。两帽拟合点为 E242.871／N154.293 与 E240.725／N175.843，轴长 21.657 米。增加角度后的两帽横向残差最大 0.17 米。南端栏杆与上排窗带另取点。所有手读像素、方位、原始相机坐标及各图指纹随控制入库。街景高度仅用于相对观察。

2021-07-29 的 89° 正眼和 2017、2022 两帧仍能看清红砖门柱、深檐底、上排长窗、沿街铺带和白蓝护栏。按两帽与栏杆交会定街侧，2021 照片上叠核显示旧足迹落在人行带和车路肩。沿用 2.32 米眼高作地面投影示意，实际划分取 EN 平面。旧 111.83 平方米约有 45.82 平方米在人行带、66.01 平方米在栏外路肩一侧。旧四角在柱面街侧约 2.90–11.57 米。2023 南眼和北眼、2021 正面眼往廊口中点的视线，分别穿旧轮廓 6.93、6.22、8.01 米。照片与叠绘原图在云端留供观察。[原图链接及手读数](registration.json) · [2021 平面叠核](evidence/history-overlap.json) · [原场景竖剖面](evidence/before/surface-profiles.json)

按旧试作的逐面指纹撤其壳体、附属及近街误位的旧试作廊。公交侧灰铺、白蓝栏、两端砖柱、连贯墙额、深檐和上排窗带用登记柱面和路边位置重做。下层只做到照片可见的门槛、窗格与遮蔽深度，公共廊沿同一坡面连续。门内、店号、精确后墙和产权仍待核。地面局部纵横高差取现有游戏可走地表，绝对标高保留待核。前廊使用项目已有许可的石、砖、混凝土和沥青材质。邻接中兴路和下回水沟原件继续作底面。[旧壳面所有权](ownership-10.json) · [原生返图及道路验证](evidence/README.md)

## 重开与试玩

用 Blender 4.3.2 打开 `zhongxing-arcade10.blend`，或从仓库根目录重建到已经创建的目录。

```sh
blender -b work/scene_r24/district_500/outer_district.blend \
  -P work/scene_r24/district_refresh/street_groups/zhongxing_arcade10/build.py -- /absolute/output
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --north-edge=10
```

场景层由正常 `first_shift.tscn` 安装，`compose.py` 在原城市组合源接入同一编辑层。Godot 4.6.3 用 `walk.gd` 实走，设置新 `CQ_QA_DIR` 并传 `--day-one-test --explore-500 --north-edge=10`。加 `--qa-without-zhongxing10-arcade` 从同一点复验父版阻挡。固定照片观测 `--arcade-camera-plan=<evidence/cameras.json>`。旧 10–12–13–22 组的历史支承脚本可用此父版开关复查 10；另用 `--qa-without-zhongxing22-finish` 复原当时的 22 支承名。

## 候车棚与街面门窗精修

按同址实物重绘站名，并制作原创牌面、透明玻璃、檐下构件及可读的门窗框。生成贴图可先运行 `python3 work/scene_r24/district_refresh/street_groups/zhongxing_arcade10/draw_stop.py work/project/chongqing_godot_v05/assets/district_500`。需要 Pillow 和 Noto Sans CJK Bold TTC。现有图、独立源及运行导出均独立留存。[新旧八机位与实际复走](evidence/stop-and-entrance/README.md)
