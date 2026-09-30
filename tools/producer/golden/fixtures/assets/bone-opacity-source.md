# Authored bone opacity assets

The two models and texture containers are unchanged selected assets from Workshop project
2998757800, `scene.pkg`. The fixture retains their original animation and geometry bytes;
its scene supplies finite frame, blend and visibility inputs to direct and effect draws.

| Asset | SHA-256 |
|---|---|
| `models/眼睛_puppet.mdl` | `f776d63f6f86532324faeb9c7c7db41716c2aabe6f873adc7dbf62673a2564e4` |
| `models/睫毛_puppet.mdl` | `1552dae6c4cd32fbdf66558dbdb4466b1c4d0b9d86d32cea93980b94dcd91876` |
| `materials/眼睛.tex` | `9fd9cd7a34e2d6205d93bf3b5499a9104c248c1d8753f77d7f5c8dcb95759724` |
| `materials/睫毛.tex` | `d3fffd2681ce78755b78b424e6cde162492330fe2092c6e6cc91e1e080d97cb0` |

Both animations run at 60 Hz with 300 intervals and 301 samples per track. The eye model
has four bones and animation 62; the eyelash model has six bones and animation 47. At
frame 20 their opacity palettes are `[0.5, 0, 0.5, 0]` and `[1, 0.5, 0, 1, 0.5, 0.5]`.
Ordinary half-weight layers mix these values with opaque. Hidden and zero-weight layers
leave opaque values. The Opacity effect and image shader sources use the configured
shared Wallpaper Engine assets.
