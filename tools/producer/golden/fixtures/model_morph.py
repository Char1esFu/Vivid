"""Observe four model chunks through finite morph curves and a normal-color material."""

import json
from pathlib import Path


STATES = [[0, 1, True, 0, 0, False], [4.5, 1, True, 0, 0, False],
          [10.25, 0.5, True, 0, 0, False], [4.5, 0.75, True, 20.5, 0.5, True],
          [20.5, 0.5, True, 4.5, 1, True], [10.25, 1, False, 4.5, 0.5, True],
          [4.5, 0, True, 20.5, 0, True], [4.5, 1, True, 0, 0, False]]


def make_fixture(assets_dir):
    # Each state remains selected for three draws. Independent animation layers exercise
    # fractional seek, signed blending, visibility and restoration on the same geometry.
    script = """'use strict';
const states = STATES;
let step = 0;
export function init(value) { thisObject.pause(); return value; }
export function update(value) {
    const phase = Math.min(states.length - 1, Math.floor(step / 3));
    const state = states[phase];
    thisObject.pause();
    thisObject.setFrame(state[INDEX]);
    thisObject.blend = state[INDEX + 1];
    console.log('ModelMorphInput', INDEX, step++, phase, state);
    return state[INDEX + 2];
}
""".replace("STATES", json.dumps(STATES))
    shader = (Path(assets_dir) / "shaders/generic4.vert").read_text()
    shader = "varying vec3 v_MorphProbeNormal;\n" + shader
    position = shader.index("#if SKINNING", shader.index("void main()"))
    # Encoding the normal explicitly makes normal deltas observable even when a scene's
    # ordinary unlit materials would produce identical colors for different normal vectors.
    shader = shader[:position] + "v_MorphProbeNormal = localNormal;\n" + shader[position:]
    files = {
        "shaders/golden/model-morph.vert": shader,
        "shaders/golden/model-morph.frag": "varying vec3 v_MorphProbeNormal;\n"
            "void main() { gl_FragColor = vec4(v_MorphProbeNormal * 0.5 + 0.5, 1.0); }\n",
    }
    for stem in ["boost_Top2", "boost1", "boost2", "boost_Top"]:
        files[f"materials/models/BoostModel/{stem}.json"] = {"passes": [{
            "shader": "golden/model-morph", "textures": [],
            "combos": {"LIGHTING": 0, "FOG": 0}, "blending": "normal",
            "cullmode": "nocull", "depthtest": "enabled", "depthwrite": "enabled",
        }]}
    layers = []
    for index in [0, 3]:
        layers.append({"id": 200 + index, "name": f"morph-{index}", "animation": 401,
                       "additive": index == 3, "blend": 1, "rate": 0,
                       "blendin": False, "blendout": False,
                       "visible": {"value": index == 0, "script": script.replace("INDEX", str(index))}})
    return {
        "description": "Four model chunks consume distinct signed morph curves and nonzero normals; "
                       "fractional seek, layer blending, visibility and reset reach actual vertex draws.",
        "docs": ["scene/scenescript/reference/class/IAnimationLayer.md", "scene/shader/overview.md"],
        "scenario": "model-morph", "asset_files": ["models/model-morph.mdl"], "files": files,
        "camera": {"eye": "0 0 1158.033737", "center": "0 0 0", "up": "0 1 0"},
        "general": {"orthogonalprojection": None, "farz": 10000, "fov": 50,
                    "clearcolor": "0.02 0.03 0.05", "cameraparallax": False},
        "objects": [{"id": 100, "name": "model-morph", "model": "models/model-morph.mdl",
                     "origin": "0 -250 0", "angles": "90 0 0", "scale": "2 2 2",
                     "visible": True, "castshadow": False, "reflected": False,
                     "animationlayers": layers}],
    }
