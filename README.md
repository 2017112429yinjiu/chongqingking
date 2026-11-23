# 重庆外卖王 · Chongqing King

200 × 200 米重庆街区外卖游戏，当前为 **R24 构建 24 内部开发版**。包含第一天师傅带教、骑行与入户送餐、午市拼送，以及通过两栋楼的楼梯和高连廊完成的穿楼托送。

## 打开项目

需要 **Git LFS、Godot 4.6.3 Forward+、Blender 4.3.2**。首次克隆请预留大型资产下载时间和磁盘空间。

```powershell
git lfs install
git clone https://github.com/2017112429yinjiu/chongqingking.git
cd chongqingking
git lfs pull
git lfs fsck
```

在 Godot 4.6.3 中导入 `work/project/chongqing_godot_v05/project.godot`，等待首次资源导入完成，按 F5。默认入口为 `first_shift.tscn`。Blender 4.3.2 的当前完整可编辑场景为 `work/scene_r24/vertical_run/city_and_crossing.blend`。

Blender 源沿用原机器的外部库路径；换目录或机器后，按[库路径说明](docs/VERSION_CONTROL.md#blender-外部库路径)重新定位到仓库内的人物库。

本地快捷入口和验证脚本使用 `work/tools/godot-4.6.3/` 及 `work/tools/blender-4.3.2-windows-x64/`；引擎安装文件不进入版本库，请自行安装到相应位置。不要用 Godot 4.7.2 自动升级工程。

## 开发资料

- [当前入口及历史版本说明](START.md)
- [开发约定](AGENTS.md) · [持续交接日志](HANDOFF_LOG.md)
- [第一天配送](work/project/chongqing_godot_v05/docs/FIRST_SHIFT.md)
- [穿楼托送及实机证据](work/project/chongqing_godot_v05/docs/VERTICAL_RUN_R24.md)
- [GitHub 版本控制及本地档案边界](docs/VERSION_CONTROL.md)

当前工程、独立制作层、脚本、资源导入设置、素材署名和原始验证记录一同管理。旧版整城快照、原始交付归档、第三方 MAX 原包、重复测试工程和引擎程序保留在原本机；精确清单见版本控制文档，克隆仓库不会取得这些本地档案。

本仓库用于私有开发备份，不代表美术验收或正式发行。第三方素材各自适用原许可；素材来源记录、署名、ODbL 数据及尚未确认的授权状态随工程保留。此仓库没有授予整个项目统一的开源许可。
