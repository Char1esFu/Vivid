"""Exercise authored eye and eyelash opacity through direct and effect publication draws."""

import json
from pathlib import Path


CASES = [(0, 1, True), (10, 1, True), (10.5, 1, True), (20, 1, True),
         (30, 1, True), (40, 1, True), (299.5, 1, True), (0, 1, True),
         (20, 0.5, True), (20, 0, True), (20, 1, False), (0, 1, True)]


def make_fixture(assets_dir):
    # Each state gets three draws so the same input observes both immediate publication
    # and a settled pose. Frame and blend changes use the animation layer's public API;
    # the final shader must obtain opacity from the owner's shared pose snapshot.
    script = """'use strict';
const states = STATES;
let step = 0;
export function init(value) {
    thisObject.pause();
    thisObject.setFrame(states[0][0]);
    return value;
}
export function update(value) {
    const phase = Math.min(states.length - 1, Math.floor(step / 3));
    const state = states[phase];
    thisObject.pause();
    thisObject.setFrame(state[0]);
    thisObject.blend = state[1];
    console.log('BoneOpacityInput', thisLayer.name, step, phase, state);
    ++step;
    return state[2];
}
""".replace("STATES", json.dumps(CASES))
    files = {}
    assets = []
    objects = []
    for row, (stem, animation) in enumerate([("眼睛", 62), ("睫毛", 47)]):
        assets.extend([f"models/{stem}_puppet.mdl", f"materials/{stem}.tex"])
        files[f"models/{stem}.json"] = {
            "autosize": True, "material": f"materials/{stem}.json",
            "puppet": f"models/{stem}_puppet.mdl"}
        files[f"materials/{stem}.json"] = {"passes": [{
            "shader": "genericimage2", "textures": [stem], "combos": {"VERSION": 2},
            "blending": "translucent", "cullmode": "nocull", "depthtest": "disabled",
            "depthwrite": "disabled"}]}
        for column, route in enumerate(["direct", "effect"]):
            owner_id = 100 + row * 2 + column
            owner = {
                "id": owner_id, "name": f"{stem}-{route}", "image": f"models/{stem}.json",
                "origin": f"{1028.16809 + column * 2047:.5f} {812.00366 + row * 1861:.5f} 0",
                "scale": "0.60472 0.60472 0.60472", "size": "1415 2047",
                "visible": True, "castshadow": False, "copybackground": False,
                "animationlayers": [{"id": owner_id + 100, "name": "opacity",
                    "animation": animation, "additive": False, "blend": 1, "rate": 1,
                    "visible": {"value": True, "script": script}}]}
            if route == "effect":
                owner["effects"] = [{"id": owner_id + 200, "name": "opacity-publication",
                    "file": "effects/opacity/effect.json", "visible": True,
                    "passes": [{"constantshadervalues": {"alpha": 1}}]}]
            objects.append(owner)
    # Object entries retain their authored effect descriptors, so supply the descriptor's
    # project-relative dependencies along with it, as an exported scene package does.
    effect_root = Path(assets_dir) / "effects/opacity"
    files["effects/opacity/effect.json"] = (effect_root / "effect.json").read_text()
    for name in ["materials/effects/opacity.json", "shaders/effects/opacity.vert",
                 "shaders/effects/opacity.frag"]:
        files[name] = (effect_root / name).read_text()
    return {
        "description": "Two original opacity animations share frame, blend and visibility inputs "
                       "across direct and effect publication draws, including fractional seek and reset.",
        "docs": ["scene/scenescript/reference/class/IAnimationLayer.md"],
        "scenario": "bone-opacity", "asset_files": assets, "files": files, "objects": objects,
        "general": {"orthogonalprojection": {"width": 4094, "height": 3722},
                    "clearcolor": "0.7 0.7 0.7", "farz": 10000}}
