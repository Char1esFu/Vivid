"""Expose script registration changing an otherwise identical sprite timeline."""

from sprite_autosize import make_fixture as make_sprite_fixture


def make_fixture(assets_dir):
    fixture = make_sprite_fixture(assets_dir)
    material = fixture["files"]["materials/golden/sprite-autosize.json"]["passes"][0]
    del material["usertextures"]
    scripts = [None, "export function update(value) { return value; }", """
export function update(value) {
    const animation = thisLayer.getTextureAnimation();
    console.log('SpriteClockObserver', animation.getFrame(), animation.isPlaying());
    return value;
}
"""]
    # All panels sample the same original clock sprite with identical size and raster
    # placement modulo horizontal translation. Neither callback controls its animation;
    # registering a property script must therefore preserve the unregistered timeline.
    for owner, name, script in zip(fixture["objects"],
                                   ["plain", "identity", "observer"], scripts):
        owner["name"] = name
        owner.pop("effects", None)
        owner["visible"] = True if script is None else {"value": True,
                                                        "script": "'use strict';\n" + script}
        fixture["files"][owner["image"]]["autosize"] = False
    fixture.pop("properties")
    fixture.update(description="Unregistered, identity-script and read-only observer sprites "
                               "share the same autoplay phase through frame boundaries.",
                   scenario="sprite-clock",
                   asset_files=["materials/selected/sprite0.tex"])
    return fixture
