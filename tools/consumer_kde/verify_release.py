#!/usr/bin/env python3
"""Check the shipped KDE plugin's library paths and runtime ABI requirements."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile


def output(*command):
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)


def verify(archive, qt_version):
    # Inspect the archive after CPack's install step. Testing the build-tree .so
    # would hide missing package files and dependencies on the build-tree RPATH.
    with tempfile.TemporaryDirectory(prefix="verify-kde-", dir=archive.parent) as stage:
        with zipfile.ZipFile(archive) as package:
            package.extractall(stage)
        plugins = list(Path(stage).glob("*/contents/ui/VividDisplayEmbed/*.so"))
        if len(plugins) != 1:
            raise RuntimeError(f"Expected one packaged QML plugin, found {plugins}")
        plugin = plugins[0]
        dynamic = output("readelf", "--dynamic", str(plugin))
        # Qt may install an $ORIGIN-relative search path for QML plugins. That is
        # relocatable; absolute SDK paths or a working-directory lookup are not.
        for search_path in re.findall(r"\((?:RPATH|RUNPATH)\).*?\[(.*?)\]", dynamic):
            for directory in search_path.split(":"):
                if directory != "$ORIGIN" and not directory.startswith("$ORIGIN/"):
                    raise RuntimeError(f"Packaged plugin retains a non-relocatable library path: {directory}")

        versions = output("readelf", "--version-info", str(plugin))
        # A release must never silently acquire the host's newer Qt, libc or C++
        # runtime. Private Qt ABIs also defeat compatibility across minor releases.
        if "PRIVATE_API" in versions:
            raise RuntimeError("Packaged plugin depends on a private Qt ABI")
        ceilings = {"Qt": tuple(map(int, qt_version.split(".")[:2])),
                    "GLIBC": (2, 39), "GLIBCXX": (3, 4, 32)}
        for family, ceiling in ceilings.items():
            required = [tuple(map(int, v.split(".")))
                        for v in re.findall(rf"\b{family}_(\d+(?:\.\d+)*)", versions)]
            if not required or max(required) > ceiling:
                raise RuntimeError(f"Unexpected {family} requirements: {sorted(set(required))}")
            print(f"Packaged {family} ABI: {'.'.join(map(str, max(required)))}", flush=True)

        dependencies = output("ldd", "-r", str(plugin))
        print(dependencies, flush=True)
        if "not found" in dependencies or "undefined symbol:" in dependencies:
            raise RuntimeError("Packaged plugin has unresolved runtime dependencies")

        print(f"Verified KDE release: {archive.name}, Qt {qt_version}", flush=True)


if __name__ == "__main__":
    verify(Path(sys.argv[1]).resolve(), sys.argv[2])
