# 余下 20 处城区刷新验收

制作父版 `cb36b07c1128acdd871923610bf6704c6ac5d57a`。清单来自正常首班场景中仍可见的 20 个旧框架，包含仍承担玩法的原构件。已有走线和互动是本次回归基线。原标识继续使用。 [运行场景清点](../evidence/current-shells/README.md) · [城区原台账与实景来源](../evidence/plots.tsv) · [本轮制作经验](METHOD.md)

## 按区域验收

| 区域 | 地块 | 核验重点 | 本轮状态 |
|---|---|---|---|
| 中兴路与照相巷 | 01 照相巷便民市场 | 从临街进主厅，接单、送达、回到街边 | [成片及实走](east/FOLLOWUP.md) |
| 中兴路与照相巷 | 12 沿街瓦檐 | 沿公开步带到檐柱外并转身 | [成片及实走](east/FOLLOWUP.md) |
| 中兴路与照相巷 | 22 圆端花池 | 两侧灰铺、圆弧压顶与树池接地 | [成片及实走](east/FOLLOWUP.md) |
| 解放西路 | 26 临街停靠边 | 街肩去回，树后真实墙脚待证 | [围合及实走](west/FOLLOWUP.md) |
| 西坡与马蹄街 | 30 西坡沿街与园边 | 两处公开面分开 | [围合及实走](west/FOLLOWUP.md) |
| 西坡与马蹄街 | 31 西坡园边 | 墙脚、园侧折返点和上缘硬铺 | [围合及实走](west/FOLLOWUP.md) |
| 西坡与马蹄街 | 34 马蹄街接出 | 墙栏、排水和公开门口外沿 | [围合及实走](west/FOLLOWUP.md) |
| 西坡与马蹄街 | 35 马蹄街上缘 | 公开石步带和挡台 | [围合及实走](west/FOLLOWUP.md) |
| 西坡与马蹄街 | 49 西坡下层 | 独立低层硬铺，保持高低层区别 | [围合及实走](west/FOLLOWUP.md) |
| 北缘与凉亭子 | 40 北缘石步带 | 低石墙、压边和贴道路沿 | [实走和返图](north/README.md) |
| 北缘与凉亭子 | 41 蔡家石堡旧石墙 | 粗石、方孔、墙脚和高低层 | [实走和返图](north/README.md) |
| 北缘与凉亭子 | 42 蔡家石堡邻段 | 匿名轮廓旁可达位置，摄影遮挡中的楼脚待证 | [实走和返图](north/README.md) |
| 北缘与凉亭子 | 43 蔡家石堡后梯 | 街侧正门和转角两跑石梯 | [实走和返图](north/README.md) |
| 北缘与凉亭子 | 45 凉亭子树井 | 树池和旧围护冲突，核对公共侧及退界 | [实走和返图](north/README.md) |
| 北缘与凉亭子 | 46 凉亭子下巷 | 公共下降段、并列石级和低侧门面可见范围 | [实走和返图](north/README.md) |
| 南区路与雷家坡 | 00 南区路车棚修理铺 | 柱间工作台、正常打气、进院及返街 | [原生近景与实走](south/repair-evidence/README.md) |
| 南区路与雷家坡 | 52 高低两层公开边 | 相邻高步道和低街外沿分开 | [实走和返图](south/README.md) |
| 南区路与雷家坡 | 53 石梯接坡 | 原石梯双向及门槛承托 | [实走和返图](south/README.md) |
| 南区路与雷家坡 | 54 雷家坡共用巷北入口 | 公开近邻与现存玩法入口分开记录 | [实走和返图](south/README.md) |
| 南区路与雷家坡 | 56 雷家坡南入口 | 复核车库碰撞阻挡及可达的共用巷 | [实走和返图](south/README.md) |

## 试玩和复核

在仓库根目录运行以下命令，从 43 的公开接头进入。把 `43` 改为表内编号可直接定位，`34-street` 从街肩走进马蹄街。01 的正常取送入口使用 `--explore-500 --outer-market`，00 的修车入口使用 `--explore-500 --repair-court`，使用 `--explore-500 --refresh-plot=00-tool-eye` 可定位到柱间工作台。进入 01 后，按 E 在摊主处取货并向另一柜台交接。

```sh
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --refresh-plot=43
```

有图形硬件时，可用 Godot 4.6.3 打开正常的 `first_shift.tscn` 并传入同样的游戏参数。原生 Linux 返图使用 Compatibility 和 Mesa llvmpipe。 [20 个定位键、实测承托和两个快捷入口](combined/plot-entries.json)。 [联合实测](combined/README.md) · [本次打开的试玩画面](combined/playable-window.png) · [04 六站梁罩](../street_groups/nanqu_rail_grade/evidence/six_station_edge_to_edge/README.md)

## 最后的同机位复查

| 区域 | 修改与登记 | 原生固定机位 |
|---|---|---|
| 东片 | [01 实扫货品与 22 石板、种植材质](east/MATERIALS.md) | [JSON 与前后 PNG](east/refinement/fixed-views.json) |
| 北片 | [42 学校门口、43 南廊与 46 下巷](north/FRONTAGES.md) | [JSON 与前后 PNG](north/refinement/fixed-views.json) |
| 南片 | [53 分层石梯与 56 在用车库](south/FRONTAGES.md) | [JSON 与前后 PNG](south/refinement/fixed-views.json) |
| 西片 | [30 窗面与 34 原街口栏顶](west/CORNERS.md) | [JSON 与前后 PNG](west/refinement/fixed-views.json) |
| 00 修车台 | [柱脚净距、原生同眼和可达斜近景](south/repair-evidence/README.md) | [JSON 与 PNG](south/repair-evidence/fixed-views.json) |

## 重建增量

在仓库根目录用 Blender 4.3.2 打开原外围源，按区域执行下列命令。区域参数可用 `east`、`west`、`jiefang`、`north`、`south`。先创建输出目录，再把 GLB、JSON 放入 `work/project/chongqing_godot_v05/assets/district_500`，把对应 BLEND 放回本目录。源文件引用项目已许可的材质。组合城从原 `city_and_patrol.blend` 在 Blender 内运行 [compose.py](../../district_500/compose.py)。

```sh
blender -b work/scene_r24/district_500/outer_district.blend \
  -P work/scene_r24/district_refresh/acceptance/build.py -- north /tmp/cq-north
```
