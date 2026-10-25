# Vivid

[English](README.md) | 简体中文

<p align="center">
  <img src="producer/resources/io.github.ayasa520.Vivid.svg" alt="Vivid 缩略图" width="160">
</p>

Vivid 是 Wallpaper Engine 的 Linux 开源重实现。

**本项目使用 VIBE CODING 开发。**

## 安装发行版

从 [GitHub Releases](https://github.com/ayasa520/Vivid/releases) 页面下载文件。
请使用 Release 附带的 Assets，不要下载 Actions 页面里的 artifact ZIP。Release Assets
已经解包，可以直接安装。

64 位 Intel/AMD 设备选择 `x86_64`，64 位 Arm 设备选择 `aarch64`。运行
`uname -m` 可以查看当前系统的架构。Vivid 需要安装 Flatpak producer（渲染端），
再根据桌面环境选择一个 consumer（桌面端）：

| 桌面环境 | Release 文件 |
| --- | --- |
| Producer 和控制界面 | `io.github.ayasa520.Vivid-<版本>-<架构>.flatpak` |
| GNOME Shell | `vivid-consumer-gnome-<版本>-<架构>.zip` |
| KDE Plasma | `vivid-consumer-kde-<版本>-<架构>.zip` |
| Hyprland、Sway、niri 及其他支持 layer-shell 的合成器 | `vivid-layer-shell-consumer-<版本>-<架构>` |

下面以 `1.0.6` 的 x86_64 文件为例。请在下载文件所在的目录运行命令。

### Producer

为当前用户安装 Flatpak bundle，然后从应用菜单或命令行启动 Vivid：

```sh
flatpak install --user ./io.github.ayasa520.Vivid-1.0.6-x86_64.flatpak
flatpak run io.github.ayasa520.Vivid
```

### GNOME Shell consumer

Release 中的 ZIP 可以直接交给 `gnome-extensions` 安装，支持 GNOME Shell 45 至
51：

```sh
gnome-extensions install --force ./vivid-consumer-gnome-1.0.6-x86_64.zip
gnome-extensions enable vivid-consumer-gnome@rikka.local
```

如果 GNOME Shell 没有加载刚安装的扩展，请注销后重新登录。

### KDE Plasma consumer

解压安装包，用 KPackage 安装，然后在“桌面和壁纸”设置中选择 **Vivid**：

```sh
vivid_kde_stage="$(mktemp -d)"
unzip ./vivid-consumer-kde-1.0.6-x86_64.zip -d "${vivid_kde_stage}"
kpackagetool6 --type Plasma/Wallpaper \
  --install "${vivid_kde_stage}/dev.rikka.vivid.consumer.kde"
```

更新已经安装的 KDE package 时，将 `--install` 换成 `--upgrade`。

### Layer-shell consumer

将可执行文件安装到当前用户的本地程序目录：

```sh
install -Dm755 ./vivid-layer-shell-consumer-1.0.6-x86_64 \
  "${HOME}/.local/bin/vivid-layer-shell-consumer"
```

先启动 producer，再运行 `vivid-layer-shell-consumer`。合成器的自启动配置见
[layer-shell consumer 指南](consumer/layer-shell/README.md)。

### 更新

从 Release 文件安装的 Flatpak bundle 和桌面 consumer 都不会随 `flatpak update`
或系统包管理器更新。新版本发布后，需要重新下载并安装这两部分：

```sh
flatpak install --user --reinstall ./io.github.ayasa520.Vivid-<版本>-<架构>.flatpak
```

KDE consumer 使用上文的 `kpackagetool6 --upgrade`，然后重启 plasmashell：

```sh
systemctl --user restart plasma-plasmashell.service
```

Producer 和 consumer 应使用同一个版本。

## 故障排查

运行 `flatpak run io.github.ayasa520.Vivid` 时，producer 日志会输出到终端。

### 壁纸全黑，日志反复出现 `WINDOW_STATE_INVALID`

Consumer 与 producer 版本不一致。旧版 consumer 握手时只协商到协议
`version=1`，新版 producer 会拒绝它发送的窗口状态。按[更新](#更新)一节把
consumer 升级到与 producer 相同的版本。

### 日志中没有 `role=consumer` 的连接

桌面 consumer 没有运行。KDE Plasma 需要在“桌面和壁纸”设置中把壁纸类型选为
**Vivid**，多显示器时每块屏幕都要设置。

### 混合显卡下黑屏，日志出现 `BIND_FAILED` 和 `EGL error 0x3003`

渲染 GPU 默认为 `auto`，会优先选择独显；桌面合成器通常运行在核显上，跨 GPU
导入 linear DMA-BUF 可能失败。在 WebUI 设置中把 **渲染 GPU** 改为驱动显示器的
那张显卡（通常是核显，例如 `/dev/dri/renderD128`）。成功时日志中协商结果为
`path=optimized-same-device`。

### 带音轨的视频壁纸停在第一帧

在 1.0.12 发行版中，视频渲染器的 GStreamer 管线由 PulseAudio 提供时钟；
音频流未开始播放时，视频会停在第一帧，日志每隔几秒出现
`playing pipeline has no appsink sample` 和 `starvation recovery`。没有音轨的
视频不受影响。源码已改为让管线使用系统时钟，并按时长限制视频队列，
需要使用包含该修复的版本。

### 3D 场景中的模型缺失或出现大量碎三角面

1.0.12 发行版中，scene 渲染器读取旧版静态模型（MDLV0004、MDLV0014）时有两个问题：

- 材质路径逐块写在每个网格前的 MDLV0004 模型会被整体丢弃，日志出现
  `static mdl has fewer prefixed material paths than chunks` 和
  `static mdl parse failed`，场景中只剩背景。
- 顶点数超过 65535 的网格使用 32 位索引，但被按 16 位读取，模型上出现大量错位的
  三角面。

两者已在 `producer/third_party/wallpaper-scene-renderer` 中修复，需要使用包含该修复的版本。

## 构建

Producer 的构建产物位于 `producer/.build`。

### Flatpak

```sh
tools/vivid.sh flatpak prefetch
tools/vivid.sh build flatpak
tools/vivid.sh flatpak run-appdir
```

`tools/vivid.sh flatpak prefetch` 会先下载并固定 Flatpak 构建所需的源文件。完成后，
可以使用缓存进行离线构建：

```sh
VIVID_FLATPAK_DISABLE_DOWNLOAD=1 tools/vivid.sh build flatpak
```

Flatpak manifest 模板位于
`producer/packaging/flatpak/io.github.ayasa520.Vivid.yml`。构建脚本会将它渲染到
`producer/.build/flatpak-manifest`。默认生成的 bundle 为
`producer/.build/io.github.ayasa520.Vivid-1.0.0-<架构>.flatpak`。

通过环境变量设置 Flatpak 软件版本：

```sh
VIVID_FLATPAK_APP_VERSION=1.0.0 \
VIVID_FLATPAK_RELEASE_DATE=2026-06-18 \
  tools/vivid.sh build flatpak
```

构建缓存位于：

- `producer/.build/flatpak-builder-state`
- `producer/.build/flatpak-builder-state/ccache`
- `producer/.build/flatpak-native-cache/native-build`
- `producer/.build/flatpak-repo/vivid-producer`

首次构建需要 `org.gnome.Sdk//49`。设置 `VIVID_FLATPAK_INSTALL_DEPS_FROM=flathub`
后，`flatpak-builder` 会自动安装缺少的 SDK。

#### 构建本地修改

Flatpak 源码固定为 `VIVID_FLATPAK_GIT_URL` 和 `VIVID_FLATPAK_GIT_BRANCH`
指定的 git commit，默认是 GitHub 上的 `main`。工作区中未提交的修改和只存在于本地的
commit 都不会进入构建，脚本只会输出一行提示。测试本地修改时，先提交到一个分支，
再让构建使用本地仓库：

```sh
VIVID_FLATPAK_GIT_URL="file://${PWD}" \
VIVID_FLATPAK_GIT_BRANCH=<分支名> \
  tools/vivid.sh build flatpak
```

Submodule 按 `.gitmodules` 中的地址和父仓库记录的 commit 获取，修改 submodule
时同样需要先提交，并确保该地址可以取到这个 commit。

#### 运行构建结果

`tools/vivid.sh flatpak run-appdir` 不需要安装 bundle，也不会覆盖已安装的版本。
它使用 `producer/.build/flatpak-run/vivid-producer` 下的独立配置，而不是
`~/.var/app/io.github.ayasa520.Vivid`，因此渲染 GPU 等设置需要重新配置（见
[故障排查](#故障排查)中的混合显卡一节）。它和已安装的版本使用同一个 socket，
不能同时运行。

### 直接运行

```sh
tools/vivid.sh build direct-run
tools/vivid.sh direct-run run
```

Direct-run 产物位于 `producer/.build/direct-run`。

### 桌面 consumer

GNOME Shell 和 KDE Plasma 使用各自的插件：

```sh
tools/vivid.sh gnome build
tools/vivid.sh kde build
```

Sway、Hyprland、labwc、river、wayfire、niri 等支持 `zwlr_layer_shell_v1` 的
Wayland 合成器使用通用 layer-shell consumer：

```sh
tools/vivid.sh layer-shell build
tools/vivid.sh layer-shell run
```

Hyprland Lua 自启动和 `hl.layer_rule`、Sway `exec`、niri 自启动的示例位于
`consumer/layer-shell/README.md` 和 `consumer/layer-shell/examples/`。GNOME 仍需安装
Shell 扩展，因为 Mutter 不支持 layer-shell。

### 清理

```sh
tools/vivid.sh clean flatpak
tools/vivid.sh clean direct-run
```

致谢：

1. [waywallen](https://github.com/waywallen)
