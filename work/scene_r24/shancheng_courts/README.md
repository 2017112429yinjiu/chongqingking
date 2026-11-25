# 山城巷送单沿线 · 仁爱堂与金马寺小学

校门、树池和院坝的下一轮实作见[校门前后对照与实走](forecourt/README.md)。下文保留首批楼位和走线记录。

从[山城巷取件台](../../沿山城巷送一单.cmd)出发，走近纸袋按 E，沿长翼抵达公共交接架再按 E。交件后，左侧可进仁爱堂两翼，沿石板路上院可进金马寺小学，经一楼山城故事馆的楼梯抵达二楼山城·时光里图书馆。取件架和收件架是游戏设置。[连续玩家实走录像](evidence/delivery_to_library.mp4)

![街面、收件院口和校舍室内](evidence/street_comparison.jpg)

## 本批地块与资料

对上一批留下的 75 块逐一量了原外墙至两条送单路线的最近距离。本批撤下 3、5、47、48 号楼及其基础和碰撞。3、5 号处在取件端道路、跨线通道一带，47、48 号处在荒野花园的坡地和园路一带。按总平面图恢复邻近的仁爱堂长翼、横翼与金马寺小学主楼。余下 71 块仍在清单，最近的 0 号修理铺距送单中心线约 34.7 米。它和 4 号均与原有玩法相连，其现实用途尚待逐址核对。[75 块逐块清单](evidence/inventory.json) · [花园设计方图文](https://mooool.com/wilderness-garden-theater-by-donehome.html)

![模型楼位和院巷](evidence/footprints.jpg)

| 对象 | 有资料支持的部分 | 游戏中采用的近似 |
| --- | --- | --- |
| 两组建筑的位置 | 更新总平面图图 3、图 8 给出院落、屋顶外缘、长短翼相交方向及学校位置。以山城巷步道折点、方向和图上比例尺就近配准，并对照航片。 | 三段外墙依屋顶投影估算。局部配准不能给出现场测绘精度。 |
| 仁爱堂 | 同址实景可见灰瓦斜屋面、红色檐线、券窗、端面圆窗与折回的横翼。游戏中行人能经过长翼进入横翼。 | 室内柱网、梁架、门洞宽度和共用地坪按外形与通行尺度推定。 |
| 金马寺小学 | 实拍可见两层校舍、木格窗、门上亮窗、临院入口和树下铺地。馆内实拍及采访给出砖柱、木书架、展示台，以及楼下故事馆、楼上图书馆的用途。 | 楼梯位置、梁柱间距、书架排列和后门接坡按游戏尺度处理。 |
| 铺地与绿化 | 校门侧补石铺院坝，留下树池，巷侧石板沿墙转角收口。西侧保留已核对的花园坡地。 | 石材规格、各处铺装与绿地边缘、局部坡高未获现场尺寸。 |

[更新项目图 3、8、13](https://bbs.co188.com/thread-10503600-1-1.html) · [渝中区仁爱堂实景](https://www.cqyz.gov.cn/zjyz/lyyz/lswh/tk/202504/t20250421_14541659.html) · [重庆日报馆内外照片](https://app.cqrb.cn/html/2022-07-21/1253645_pc.html) · [楼层用途采访](https://www.cqnews.net/1/detail/1270122359964934144/web/content_1270122359964934144.html) · [山城巷步道及署名](https://www.openstreetmap.org/way/734116601)

原图可在原发布方查看。图像作者、原图指纹、材质来源及用法记录在[图像记录](reference_images.json)和[配准记录](registered.json)中。示意图与实机截图在本轮生成。

## 实走与复开

使用 Godot 4.6.3 正常 first_shift 场景和同一个玩家角色，在取件台按 E，主线步行 83.51 米，按 E 签收，再步行 53.77 米到二楼书架。整段未重置位置。录像按每 9 个物理帧采一帧、以原时间播放。另一轮独立测试走了支线，去程 93.85 米，回程 93.80 米，两次签收分别核对只有一笔入账。[连续输入记录](evidence/continuous_take.json) · [双线签收记录](evidence/handoff.json)

| 实机往返 | 去程 | 回程 |
| --- | ---: | ---: |
| 收件院口至仁爱堂横翼 | 31.89 米 | 32.08 米 |
| 收件院口经校舍穿至后门外 | 52.31 米 | 52.20 米 |
| 校内过楼梯至二楼 | 14.61 米 | 14.70 米 |

[院巷与室内 9 项](evidence/court_walk.json) · [山城巷全段双向](evidence/walk_mapped.json) · [既有共用巷道 90 项](evidence/shared_paths.json) · [旧楼穿堂与房间](evidence/halls.json) · [原存档检查](evidence/checkpoints.json) · [Blender 4.3.2 复开与模型角点](evidence/blender.json)

首轮校门视线在 0.88 米处、院口视线在 0.99 米处命中同一旧远景体块。撤下重复体块后按固定机位重拍。初版校舍后门接坡移动出现约 0.31 米的单帧跃变，之后重做后门外踏步；首轮碰撞检查也因仅查有属主的节点漏报三个运行时碰撞体，修正后逐体重查。复核楼层用途后将图书馆移至二楼并接通内梯。[原遮挡画面](evidence/first_obstructed_view.png) · [视线命中](evidence/first_sightlines.json) · [首轮步行](evidence/first_walk.json)

原 200 米城区在这次制作提交的独立巡检 authentic_courts_release_02 中，导师走完 14 条双向路线，玩家走完 26 条地面骑行路线的去回程，六处院口梯坎完成 18 次步行往返。同次三个旧城机位各采 150 帧，机型和内部分辨率写在采样文件中。[旧城巡检汇总](evidence/patrol_25b.json) · [三个旧城机位计时](evidence/original_district_timing.json)

## 可编辑工程与复验

[本批 Blender 源](delivery_courts.blend)保留两翼、校舍、结构、家具和铺地。[新区地形源](../district_500/outer_district.blend)保留旧建筑退场后的地形。运行端使用 historic_courts.glb 与 outer_district.glb，并在正常城区创建通行碰撞。

重新制作用 register.py 按原图像素与步道坐标生成 registered.json，在 Blender 4.3.2 后台执行 district_500/build.py 生成新区地形，再打开其 outer_district.blend 执行本目录 architecture.py 导出独立增量。整城编辑时从 district_patrol/city_and_patrol.blend 执行 district_500/compose.py。重建后可运行 inventory.py 更新清单。以上 Python 数据处理使用 NumPy。

从仓库根目录运行以下命令复验。工具可在 PATH 中，或用 --godot 与 --blender 指定可执行文件绝对路径。每次使用新目录。有显示设备时加 --capture，可取得连续玩家画面和八个原生机位。在 Windows 深目录复验可加 --user-data .cloud-dev/qa01，使用短的独立缓存路径。

```sh
python work/scene_r24/shancheng_courts/verify.py --output .cloud-dev/shancheng-courts/new-survey --capture
```
