"""Observe frame-sized autosize during sprite replacement and authored resets."""

from pathlib import Path


def make_fixture(assets_dir):
    script = """'use strict';
export function update(value) {
    const animation = thisLayer.getTextureAnimation();
    animation.stop();
    animation.setFrame(0);
    return value;
}
"""
    files = {
        "shaders/golden/sprite-autosize.vert":
            (Path(assets_dir) / "shaders/genericimage4.vert").read_text(),
        "shaders/golden/sprite-autosize.frag": """uniform sampler2D g_Texture0;
varying vec4 v_TexCoord;
void main() {
    float alpha = texSample2D(g_Texture0, v_TexCoord.xy).a;
    gl_FragColor = vec4(0.4 + alpha * 0.1, 0.5, 0.6, 1.0);
}
""",
        "materials/golden/sprite-autosize.json": {"passes": [{
            "shader": "golden/sprite-autosize", "textures": ["selected/sprite0"],
            "usertextures": [{"name": "spritefile"}], "blending": "translucent",
            "combos": {"spritesheet": 1, "LIGHTING": 0},
            "cullmode": "nocull", "depthtest": "disabled", "depthwrite": "disabled",
        }]},
        "effects/golden/sprite-identity.json": {"passes": [{
            "material": "materials/effects/opacity.json",
        }]},
    }
    opacity = Path(assets_dir) / "effects/opacity"
    for relative in ["materials/effects/opacity.json", "shaders/effects/opacity.vert",
                     "shaders/effects/opacity.frag"]:
        files[relative] = (opacity / relative).read_text()
    owners = []
    # The opaque diagnostic card retains a sampled-alpha consumer while making its full
    # geometry observable. Two autosize paths share inputs with a fixed-size control.
    for index, (name, x, effect, autosize) in enumerate([
            ("effect", 480, True, True), ("direct", 960, False, True),
            ("fixed", 1440, False, False)]):
        model = f"models/golden/sprite-autosize-{name}.json"
        files[model] = {"material": "materials/golden/sprite-autosize.json", "autosize": autosize}
        owner = {"id": 395 + index, "name": name, "image": model,
                 "size": "256 128", "origin": f"{x} 540 0", "scale": "1 1 1",
                 "angles": "0 0 0", "color": "1 1 1", "alpha": 1, "brightness": 1,
                 "parallaxDepth": "0 0", "castshadow": False, "clampuvs": True,
                 "visible": {"value": True, "script": script}}
        if effect:
            owner["effects"] = [{"id": 500, "name": "sprite-identity", "visible": True,
                "file": "effects/golden/sprite-identity.json",
                "passes": [{"constantshadervalues": {"alpha": 1}}]}]
        owners.append(owner)
    return {
        "description": "Sprite frame dimensions resize direct and effect cards on replacement; "
                       "repeated values, authored resets and fixed-size control remain observable.",
        "docs": ["scene/scenescript/reference/class/ITextureAnimation.md"],
        "scenario": "sprite-autosize",
        "asset_files": ["materials/selected/sprite0.tex", "materials/selected/sprite1.tex"],
        "files": files, "objects": owners,
        "general": {"clearcolor": "0.02 0.03 0.04", "hdr": False},
        "properties": {"spritefile": {"type": "file", "value": "selected/sprite0"}},
    }
