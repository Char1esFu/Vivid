# Vivid Consumer KDE

This directory contains a Plasma 6 display consumer package for the existing
display-v1 transport.

The package embeds its Qt QML display module under
`contents/ui/VividDisplayEmbed/`, so the wallpaper can carry the display
library `.so` inside the extension package instead of depending on a
system-wide QML module.

The consumer does not force a Qt Quick graphics API. It detects the scene-graph
API chosen by Plasma and selects the matching EGL or Vulkan DMA-BUF importer.

## Build

```sh
tools/vivid.sh kde build
```

## Install For The Current User

```sh
tools/vivid.sh kde install
```

After upgrading the QML display module, restart plasmashell so Qt reloads the
plugin from the package:

```sh
systemctl --user restart plasma-plasmashell.service
```

## Package

```sh
tools/vivid.sh kde zip
```

To override the package version:

```sh
VIVID_CONSUMER_PACKAGE_VERSION=1.2.3 tools/vivid.sh kde zip
```

Release CI runs the same `tools/vivid.sh kde zip` command in Ubuntu 24.04 on
native x86_64 and aarch64 runners. It first downloads the complete Qt 6.8.3 SDK
and builds KScreen 6.3.6 with that SDK under `.build`. These build dependencies are
not bundled into the wallpaper package; the desktop supplies Qt and KScreen at runtime.
Prebuilt packages target Qt 6.8 or newer and libKF6Screen.so.8. CI also rejects
symbol requirements newer than Ubuntu 24.04's glibc 2.39 and GCC 13 C++ runtime
(GLIBCXX_3.4.32). Local builds continue to use the dependencies installed on the
build machine.

After packaging, CI checks the ZIP's library paths, symbol versions and plugin
dependencies before uploading it. These build checks do not exercise wallpaper
rendering inside a Plasma session.
