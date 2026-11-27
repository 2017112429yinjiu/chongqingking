# R24 Linux 500 米试作末批复测

游戏正式版本 bb91ddda0823942662bf9941b3e61fd10e5a1ae0。在独立临时卷执行 Linux 同入口巡检。原始路径名为 cq500-r24-allroads-software-stills-G8abNPjP。

地面登记 30 路，其中 26 条露天行车。完成 16004 个道路断面和 10000 个网格点，旧标高短量未命中 28 个，由 north 项逐点再量。

- out 三批合计 26/26 路通过，独立 road ID 26，未通过 ID 无。
- back 三批合计 26/26 路通过，独立 road ID 26，未通过 ID 无。

导师路段 20/20，全长 2721.58 米。官方汇总器退出 1。

| 入口 | 退出码 | 检查 | 引擎 ERROR 行数 |
| --- | ---: | ---: | ---: |
| bridge | 0 | 42/42 | 0 |
| counter | 0 | 7/7 | 0 |
| ground | 0 | 见运行输出 | 0 |
| home | 0 | 13/13 | 0 |
| junction_profiles | 0 | 67/67 | 0 |
| lunch | 0 | 35/35 | 0 |
| market | 0 | 5/5 | 0 |
| north | 0 | 45/45 | 0 |
| older_crossings | 0 | 19/19 | 0 |
| pavement | 0 | 10/10 | 0 |
| player_back_0 | 0 | 见运行输出 | 0 |
| player_back_1 | 0 | 见运行输出 | 0 |
| player_back_2 | 0 | 见运行输出 | 0 |
| player_out_0 | 0 | 见运行输出 | 0 |
| player_out_1 | 0 | 见运行输出 | 0 |
| player_out_2 | 0 | 见运行输出 | 0 |
| repair | 0 | 10/10 | 0 |
| restore | 0 | 5/5 | 0 |
| ride | 137 | 见运行输出 | 0 |
| sections | 0 | 3/3 | 0 |
| shancheng | 0 | 12/12 | 0 |
| single | 0 | 8/8 | 0 |
| sites | 0 | 15/15 | 0 |
| teaching | 0 | 85/85 | 0 |
| timing | 124 | 见运行输出 | 0 |
| turns | 0 | 7/7 | 0 |

可视阶段使用 Linux Xvfb、OpenGL Compatibility 与 Mesa 软件渲染。引擎日志中的退出清理问题单列，Windows 专用脚本的 ERROR 闸门会看这些真实行。

计时记录未产出。单项退出码为 124。

[逐项压缩前统计](actual-summary.json) · [地面原始记录](ground/district.json) · [北缘记录](north/north.json) · [Windows入口参数来源](../../../district_patrol/verify.ps1)

同一制作 SHA 的原导师入口以无头模式补跑 28/28 段，3453.86 米。软件原生导师失败和已完成路段留在 ride。跨运行物理覆盖汇总退出 0。

[无头导师原始数据](mentor-headless/patrol.json) · [分条件汇总](mentor-recovery-summary.json)

同一软件引擎短取样。场景加载和机位定位期间关闭渲染循环。每处恢复连续渲染，预热四帧后量八帧墙钟间隔。

- switchback 墙钟中位数 14781.057 毫秒。
- crossing 墙钟中位数 18967.574 毫秒。
- 301 墙钟中位数 17265.546 毫秒。

[软件短取样和实际窗口](timing-software-sparse/sparse-timing.json)

正式连续 150 帧及连续 24 帧两次均超时。八帧补测窗口为 1152×648，内部视口为 692×389。原超时包装器在延时后记录退出 124，实际引擎写出了三处各八帧的完整记录。

[原时限延长记录](timing-software-sparse/runtime-extension.txt) · [标准计时退出码](timing/exit-code.txt) · [24 帧补测退出码](timing-software-short/exit-code.txt)
