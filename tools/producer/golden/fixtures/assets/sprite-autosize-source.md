# Sprite autosize fixture sources

Both textures retain their original bytes and frame tables.

- `materials/selected/sprite0.tex`: Workshop `3369989878`, original
  `materials/workshop/3219510589/clockHideToggle.tex`; SHA-256
  `48ae375bae9d250cd3dba9b295180840cbab96b02eb193277997cfd267057044`.
  Three 256×128 frames in one 256×384 atlas.
- `materials/selected/sprite1.tex`: Workshop `3701356561`, original
  `materials/workshop/3695990817/dayNightToggleSprite.tex`; SHA-256
  `c27887fca2338c94bac5db41fc11ef15fde9324b4fb6e36b217c28438edcafef`.
  Three 256×256 frames in one 256×768 atlas.

The fixture explicitly authors file-property replacement, frame-zero selection,
two autosize consumers and a fixed-size control. Its opaque material samples the
original alpha while exposing the display-card boundary. This input does not
describe the original wallpapers' scripts or material appearance.
