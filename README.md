# Vivid

[English](README.md) | [简体中文](README.zh-CN.md)

<p align="center">
  <img src="producer/resources/io.github.ayasa520.Vivid.svg" alt="Vivid thumbnail" width="160">
</p>

Vivid is an open-source reimplementation of Wallpaper Engine for Linux.

**THIS PROJECT USES VIBE CODING.**

## Install a release

Download files from the [GitHub Releases](https://github.com/ayasa520/Vivid/releases)
page. Use the assets attached to a release, not the artifact ZIPs from the
Actions page. Release assets are already unpacked into installable files.

Choose `x86_64` for 64-bit Intel/AMD systems or `aarch64` for 64-bit Arm
systems. `uname -m` prints the architecture of the current system. Each Vivid
installation needs the Flatpak producer and one consumer matching the desktop:

| Desktop | Release asset |
| --- | --- |
| Producer and controller | `io.github.ayasa520.Vivid-<version>-<arch>.flatpak` |
| GNOME Shell | `vivid-consumer-gnome-<version>-<arch>.zip` |
| KDE Plasma | `vivid-consumer-kde-<version>-<arch>.zip` |
| Hyprland, Sway, niri, and other layer-shell compositors | `vivid-layer-shell-consumer-<version>-<arch>` |

The commands below use the `1.0.6` x86_64 assets as examples. Run them from the
directory containing the downloaded files.

### Producer

Install the Flatpak bundle for the current user, then start Vivid from the
application launcher or the command line:

```sh
flatpak install --user ./io.github.ayasa520.Vivid-1.0.6-x86_64.flatpak
flatpak run io.github.ayasa520.Vivid
```

### GNOME Shell consumer

The release ZIP is ready for `gnome-extensions` and supports GNOME Shell 45
through 51:

```sh
gnome-extensions install --force ./vivid-consumer-gnome-1.0.6-x86_64.zip
gnome-extensions enable vivid-consumer-gnome@rikka.local
```

Log out and back in if GNOME Shell has not loaded the newly installed
extension.

### KDE Plasma consumer

Extract the package, install it with KPackage, then select **Vivid** in
**Desktop and Wallpaper** settings:

```sh
vivid_kde_stage="$(mktemp -d)"
unzip ./vivid-consumer-kde-1.0.6-x86_64.zip -d "${vivid_kde_stage}"
kpackagetool6 --type Plasma/Wallpaper \
  --install "${vivid_kde_stage}/dev.rikka.vivid.consumer.kde"
```

Use `--upgrade` instead of `--install` when updating an existing KDE package.

### Layer-shell consumer

Install the executable in the user-local binary directory:

```sh
install -Dm755 ./vivid-layer-shell-consumer-1.0.6-x86_64 \
  "${HOME}/.local/bin/vivid-layer-shell-consumer"
```

Start the producer first, then run `vivid-layer-shell-consumer`. See the
[layer-shell consumer guide](consumer/layer-shell/README.md) for compositor
autostart configuration.

### Updating

Flatpak bundles and desktop consumers installed from release files are not
updated by `flatpak update` or the system package manager. Download and
install both parts again when a new release is published:

```sh
flatpak install --user --reinstall ./io.github.ayasa520.Vivid-<version>-<arch>.flatpak
```

Upgrade the KDE consumer with `kpackagetool6 --upgrade` as shown above, then
restart plasmashell:

```sh
systemctl --user restart plasma-plasmashell.service
```

Keep the producer and consumer on the same version.

## Troubleshooting

`flatpak run io.github.ayasa520.Vivid` prints the producer log to the terminal.

### Black wallpaper with repeated `WINDOW_STATE_INVALID` errors

The consumer and producer versions do not match. An older consumer only
negotiates protocol `version=1`, and a newer producer rejects its window state.
Upgrade the consumer to the producer's version as described in
[Updating](#updating).

### No `role=consumer` connection in the log

The desktop consumer is not running. In KDE Plasma, select **Vivid** as the
wallpaper type in **Desktop and Wallpaper** settings, on every screen.

### Black screen on hybrid graphics with `BIND_FAILED` and `EGL error 0x3003`

The default rendering GPU, `auto`, prefers the discrete GPU, while the
compositor usually runs on the integrated GPU, and importing a linear DMA-BUF
across GPUs can fail. In the WebUI settings, set **Rendering GPU** to the GPU
that drives the display, usually the integrated one such as
`/dev/dri/renderD128`. A working setup logs `path=optimized-same-device`.

### Video wallpapers with an audio track freeze on the first frame

In release 1.0.12, the video renderer's GStreamer pipeline takes its
clock from PulseAudio. While the audio stream has not started, video stays on
the first frame and the log prints `playing pipeline has no appsink sample` and
`starvation recovery` every few seconds. Videos without audio are not affected.
The source now pins the pipeline to the system clock and bounds the video queue
by time; use a build that includes this fix.

### Models missing or covered in broken triangles in 3D scenes

In release 1.0.12, the scene renderer has two problems reading legacy static
models (MDLV0004 and MDLV0014):

- MDLV0004 models that store a material path in front of each mesh chunk are
  dropped entirely. The log prints
  `static mdl has fewer prefixed material paths than chunks` and
  `static mdl parse failed`, and only the background is shown.
- Meshes with more than 65535 vertices store 32-bit indices but are read as
  16-bit, which covers the model in misplaced triangles.

Both are fixed in `producer/third_party/wallpaper-scene-renderer`; use a build
that includes the fix.

## Build

Producer build artifacts are written under `producer/.build`.

### Flatpak

```sh
tools/vivid.sh flatpak prefetch
tools/vivid.sh build flatpak
tools/vivid.sh flatpak run-appdir
```

`tools/vivid.sh flatpak prefetch` downloads and pins the Flatpak sources first.
After that, an offline/cached build can be run with:

```sh
VIVID_FLATPAK_DISABLE_DOWNLOAD=1 tools/vivid.sh build flatpak
```

The Flatpak manifest is rendered from
`producer/packaging/flatpak/io.github.ayasa520.Vivid.yml` into
`producer/.build/flatpak-manifest`. The bundle is written to
`producer/.build/io.github.ayasa520.Vivid-1.0.0-<arch>.flatpak` by default.

Set the Flatpak software version with:

```sh
VIVID_FLATPAK_APP_VERSION=1.0.0 \
VIVID_FLATPAK_RELEASE_DATE=2026-06-18 \
  tools/vivid.sh build flatpak
```

Useful cache locations:

- `producer/.build/flatpak-builder-state`
- `producer/.build/flatpak-builder-state/ccache`
- `producer/.build/flatpak-native-cache/native-build`
- `producer/.build/flatpak-repo/vivid-producer`

The first build needs `org.gnome.Sdk//49`. Set
`VIVID_FLATPAK_INSTALL_DEPS_FROM=flathub` to let `flatpak-builder` install a
missing SDK.

#### Building local changes

The Flatpak source is pinned to the git commit selected by
`VIVID_FLATPAK_GIT_URL` and `VIVID_FLATPAK_GIT_BRANCH`, which default to `main`
on GitHub. Uncommitted changes and local-only commits are not built; the script
only prints a notice. To test local changes, commit them to a branch and build
from the local repository:

```sh
VIVID_FLATPAK_GIT_URL="file://${PWD}" \
VIVID_FLATPAK_GIT_BRANCH=<branch> \
  tools/vivid.sh build flatpak
```

Submodules are fetched from the URL in `.gitmodules` at the commit recorded by
the parent repository, so submodule changes must also be committed and
reachable from that URL.

#### Running the build

`tools/vivid.sh flatpak run-appdir` runs the build without installing the
bundle or replacing an installed version. It keeps its own configuration under
`producer/.build/flatpak-run/vivid-producer` instead of
`~/.var/app/io.github.ayasa520.Vivid`, so settings such as the rendering GPU
must be configured again (see the hybrid graphics entry in
[Troubleshooting](#troubleshooting)). It uses the same socket as the installed
version, so the two cannot run at the same time.

### Direct Run

```sh
tools/vivid.sh build direct-run
tools/vivid.sh direct-run run
```

Direct-run artifacts stay in `producer/.build/direct-run`.

### Desktop consumers

GNOME Shell and KDE Plasma have dedicated plugins:

```sh
tools/vivid.sh gnome build
tools/vivid.sh kde build
```

Other Wayland compositors that speak `zwlr_layer_shell_v1` (Sway, Hyprland, labwc, river, wayfire, niri, …) use the catch-all client:

```sh
tools/vivid.sh layer-shell build
tools/vivid.sh layer-shell run
```

See `consumer/layer-shell/README.md` and `consumer/layer-shell/examples/` for Hyprland Lua autostart / `hl.layer_rule`, Sway `exec`, and niri autostart. GNOME still needs the Shell extension; Mutter does not implement layer-shell.

### Clean

```sh
tools/vivid.sh clean flatpak
tools/vivid.sh clean direct-run
```

Credits:

1. [waywallen](https://github.com/waywallen)
