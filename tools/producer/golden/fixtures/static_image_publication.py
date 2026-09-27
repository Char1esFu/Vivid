"""An original indexed image crop with finite effect visibility and a direct color control."""


def make_fixture():
    def material(shader):
        return {"passes": [{"shader": shader, "textures": [], "blending": "normal",
                            "cullmode": "nocull", "depthtest": "disabled", "depthwrite": "disabled"}]}

    source_vertex = """attribute vec3 a_Position;
uniform mat4 g_ModelViewProjectionMatrix;
void main() {
    gl_Position = mul(vec4(a_Position, 1.0), g_ModelViewProjectionMatrix);
}
"""
    # A UV-positioned effect deliberately fills its texture target. Only the subsequent
    # publication draw should place the original crop mesh in the scene. The right panel
    # uses no effect and independently selects the same finite colors by scenario time.
    files = {
        "shaders/static-source.vert": source_vertex,
        "shaders/static-control.vert": source_vertex,
        "shaders/static-source.frag": "void main() { gl_FragColor = vec4(1.0, 0.25, 0.0, 1.0); }\n",
        "shaders/static-final.vert": """attribute vec2 a_TexCoord;
void main() { gl_Position = vec4(2.0 * a_TexCoord - 1.0, 0.5, 1.0); }
""",
        "shaders/static-final.frag": "void main() { gl_FragColor = vec4(0.0, 0.5, 1.0, 1.0); }\n",
        "shaders/static-control.frag": """uniform float g_Time;
void main() {
    int phase = min(3, int(floor((g_Time * 30.0 - 0.5) / 10.0)));
    bool visible = phase == 1 || phase == 3;
    gl_FragColor = visible ? vec4(0.0, 0.5, 1.0, 1.0) : vec4(1.0, 0.25, 0.0, 1.0);
}
""",
        "materials/static-source.json": material("static-source"),
        "materials/static-control.json": material("static-control"),
        "materials/static-final.json": material("static-final"),
        "models/static-source.json": {"material": "materials/static-source.json",
                                      "puppet": "models/static-image-crop.mdl", "autosize": True},
        "models/static-control.json": {"material": "materials/static-control.json",
                                       "puppet": "models/static-image-crop.mdl", "autosize": True},
        "effects/static-final.json": {"version": 1, "name": "Static mesh final effect",
                                      "passes": [{"material": "materials/static-final.json"}]},
        "static-image-expectations.json": {
            "source_project": "3513007011", "source_asset": "models/图层 53_puppet.mdl",
            "source_sha256": "2a8d79f1816514411983fbc6538ed846e78778add6ea71ad6bb37ae6dc67aa03",
            "query_owner": 2480, "control_owner": 2481, "vertices": 25, "indices": 69,
            "effect_states": [False, True, False, True], "control_pixel_offset": [480, 0]},
    }
    cycle = """'use strict';
const states = [false, true, false, true];
let step = 0;
export function update(value) {
    if (step % 10 === 0) {
        const phase = Math.min(3, Math.floor(step / 10));
        thisLayer.getEffect('static-final').visible = states[phase];
        console.log('StaticMeshEffect', step, phase, states[phase]);
    }
    ++step;
    return value;
}
"""
    objects = [
        {"id": 2710, "name": "crop-parent", "origin": "216.25092 956.22217 0",
         "scale": "0.93808 1 1", "visible": True},
        {"id": 2711, "name": "control-parent", "origin": "1176.25092 956.22217 0",
         "scale": "0.93808 1 1", "visible": True},
    ]
    for control in (False, True):
        owner = {"id": 2481 if control else 2480, "name": "crop-control" if control else "crop-query",
                 "image": "models/static-control.json" if control else "models/static-source.json",
                 "parent": 2711 if control else 2710, "origin": "20.29438 5.58207 0",
                 "angles": "0 0 0.22997", "scale": "1.75065 1.01000 1", "size": "720 960",
                 "castshadow": False, "parallaxDepth": "0 0", "visible": True}
        if not control:
            owner["visible"] = {"value": True, "script": cycle}
            owner["effects"] = [{"id": 2483, "name": "static-final",
                                 "file": "effects/static-final.json", "visible": False}]
        objects.append(owner)
    return {"description": "Static indexed crop meshes retain placement when effects become visible, "
                           "hide again and restore; a direct mesh provides independent color control.",
            "docs": ["scene/shader/overview.md"], "scenario": "fixture-static-image",
            "asset_files": ["models/static-image-crop.mdl"], "general": {"clearcolor": "0 0 0"},
            "files": files, "objects": objects, "layers": []}
