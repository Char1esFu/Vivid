"""Global row budgets across explicit paragraphs and width-driven line breaks."""


def make_fixture():
    cases = [
        ("plain", "FIRST\nSECOND", 1, False, 360),
        ("marker", "FIRST\nSECOND", 1, True, 360),
        ("wrapped", "AAAA BBBB CCCC\nDDDD", 2, False, 200),
        ("wrapped-marker", "AAAA BBBB CCCC\nDDDD", 2, True, 200),
        ("marker-fit", "ABCDEF\nHIDDEN", 1, True, 180),
        ("zero", "FIRST\nSECOND\nTHIRD", 0, False, 360),
        ("width-only", "AAAA BBBB CCCC", 0, False, 200),
        ("empty-row", "\nFIRST\nSECOND", 2, False, 360),
        ("existing-marker", "FIRST…\nSECOND", 1, True, 360),
        ("color-cluster", "❤️A\nSECOND", 1, True, 360),
        ("live", "LIVE\nSECOND\nTHIRD", 1, False, 360),
    ]
    objects = []
    for index, (name, text, rows, marker, width) in enumerate(cases):
        owner = {
            "id": 600 + index, "name": name, "text": text,
            "font": "DejaVu Sans Mono", "pointsize": 12,
            "origin": f"{80 + index % 4 * 460} {980 - index // 4 * 320} 0",
            "angles": "0 0 0", "scale": "1 1 1", "color": "1 1 1",
            "alpha": 1, "brightness": 1, "horizontalalign": "left",
            "verticalalign": "top", "anchor": "none", "padding": 0,
            "depthtest": "disabled", "visible": True, "limitwidth": True,
            "maxwidth": width, "limitrows": name != "width-only",
            "maxrows": rows, "limituseellipsis": marker,
        }
        if name == "color-cluster":
            owner["font"] = "fonts/TwemojiMozilla.ttf"
        if name == "live":
            owner["text"] = {"value": text, "script": """'use strict';
let step = 0;
export function update(value) {
    const phase = Math.min(5, Math.floor(step++ / 10));
    if ((step - 1) % 10 === 0) {
        thisLayer.maxrows = [1, 2, 0, 1, 1, 1][phase];
        thisLayer.limitrows = phase !== 4;
        thisLayer.maxwidth = phase === 3 ? 180 : 360;
        console.log('TextRowsFixture', phase, thisLayer.maxrows, thisLayer.limitrows,
                    thisLayer.maxwidth, value === 'LIVE\\nSECOND\\nTHIRD');
    }
    return value;
}
"""}
        objects.append(owner)
    prefix = "INFO SceneScript log: TextRowsFixture"
    states = [(1, "true", 360), (2, "true", 360), (0, "true", 360),
              (1, "true", 180), (1, "false", 360), (1, "true", 360)]
    return {
        "description": "Global text rows, optional ellipsis, wrapped rows and live budget restoration.",
        "docs": ["scene/scenescript/reference/class/ITextLayer.md"],
        "scenario": "text-row-limit",
        "objects": objects,
        "log_expectations": {prefix: [f"{prefix} {i} {r} {enabled} {w} true"
                                      for i, (r, enabled, w) in enumerate(states)]},
    }
