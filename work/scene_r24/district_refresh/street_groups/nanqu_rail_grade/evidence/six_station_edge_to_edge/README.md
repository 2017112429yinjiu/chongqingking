# 04 南区路六站横跨复核

用 `cb36b07c` 的正常首班场景复跑 2023-05-15 同车六站的 110° 机位。首、二、末站的车道中线分别在 N−70.926／−79.782、N−78.526／−87.382、N−84.878／−93.734 米穿过轨道近远缘。[测试配置](guide.json) · [矩阵和原生图 SHA-256](result.json)

Blender 4.3.2 重开，现用箱梁最北 N−45.439 米，声屏罩最北 N−47.985 米。每站在梁纵向取五条陆侧至江侧横线，两件网格各通过 30/30，沿线的水平投影没有间隙。Godot 4.6.3 正常场景竖向上射和下射各 90/90，均命中同一个箱梁碰撞体。箱梁与罩体各有一个可见实例，均在 `NanjimenBridgePark` 下。前置桥源的构件由当前场景中的同名网格替换。此次复核保留现用资产和碰撞。[每条横线和间隙](continuous-edge-to-edge.json) · [命中与实例数](result.json)

Godot 4.6.3、Mesa llvmpipe Compatibility、700×440。1–3 站的陆侧端由树遮挡，4–5 站的梁和罩横贯画幅，6 站进入梁下后，梁底横贯画幅，罩随视角移至右上角。六张重新采集同矩阵图分别与下列归档原图相差 0–200 像素。[逐帧像素差](published-pixel-differences.json)

| 站 | 归档原生图 |
|---|---|
| 1 | [2922191AU](../high_crowns04/after/pano-2922191AU-regraded-eye.png) |
| 2 | [2924863AU](../high_crowns04/after/pano-2924863AU-regraded-eye.png) |
| 3 | [2926254AU](../high_crowns04/after/pano-2926254AU-regraded-eye.png) |
| 4 | [2927597AU](../landside04/after/pano-2927597AU-regraded-eye.png) |
| 5 | [2928988AU](../landside04/after/pano-2928988AU-regraded-eye.png) |
| 6 | [2930784AU](../landside04/after/pano-2930784AU-regraded-eye.png) |

在本目录的上两级运行 `blender -b nanqu-rail-grade.blend -P check_mesh_continuity.py -- evidence/six_station_edge_to_edge/guide.json /tmp/cq04-span.json` 可重测横线投影。Godot 可用同一配置传入 `survey.gd --rail-guide=<guide.json>`。
