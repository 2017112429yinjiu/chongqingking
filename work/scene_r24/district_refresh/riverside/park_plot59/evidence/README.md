# 59 号退楼与浅砂园路复测

两组原生同机位使用相同的镜头中心、指向和视野。第一组为 205° 的登记街景机位，第二组从长滨路公园侧步行带朝原 59 中心看。基线从桥梁批 `23a4566a` 回读，59 原房与桥梁均在场。 [205° 改前](street-205-before.png) · [205° 改后](street-205-after.png) · [街边近机位改前](park-from-roadside-before.png) · [街边近机位改后](park-from-roadside-after.png)

- 旧旋转轮廓约 116.09 平方米。原中心命中 7.190 米高的框架，改后命中 0.614 米高的连续灰铺和其下地面。新铺地含约 69.17 平方米浅砂、49.47 平方米浅蓝硬地、68.88 平方米灰铺广场。足迹、其他铺面、两处树池和四类材质接触点逐项登记。 [地面和 Blender 重开记录](ground_and_reopen.json)
- 从公园侧临街步行带起步，距道路 59146737 轴线 7.658 米。旧版在 4.235 米处撞 `COL_Outer500_Building_envelopes`，只到第一个路点。新版去程 14.626 米、回程 14.606 米，两向各 6/6 路点，24/24 地表探针通过。玩家在浅砂区同一终点转身，原路回到距初始平面约 7 厘米的位置。 [旧版失败](old-wall-blockage.json) · [新版往返](walk.json) · [玩家在浅砂回看街口](from-sand-back-to-street.png)

Godot 4.6.3 的原生帧用 Mesa llvmpipe Compatibility 采集。近机位初次被角色衣物挡住，原始输出留在云端。用同一个侧方机位重新拍摄基线和新版。软件退出时有两条 GL 纹理回收告警，所列返图保存成功。街景、原始报纸及正射瓦片只进入本地参考目录。 [主机位与原生走测](native-after.json) · [近机位补拍](roadside-camera-recapture.json) · [桥梁批走测回归](regression-bridge-walk.json) · [61 号单独观察](plot61-observation.json)
