"""Expose script registration changing an otherwise identical sprite timeline."""

import copy

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
        owner["origin"] = owner["origin"].replace(" 540 ", " 360 ")
    # Keep the registration controls in the first row. The second row observes a
    # shared timeline while one reader is hidden and another detaches, stops and
    # rejoins. Each resumed reader must match the uninterrupted peer at its position.
    shared_scripts = [None, """let step = 0;
export function update(value) { return step++ >= 35; }
""", """let step = 0;
export function update(value) {
    if (step === 5) {
        thisLayer.getTextureAnimation().stop();
        console.log('SpriteClockDetached', step);
    }
    if (step === 65) {
        thisLayer.getTextureAnimation().join();
        console.log('SpriteClockJoined', step);
    }
    ++step;
    return value;
}
"""]
    shared_owners = []
    for index, (owner, script) in enumerate(zip(fixture["objects"], shared_scripts)):
        shared = copy.deepcopy(owner)
        shared["id"] = 398 + index
        shared["name"] = ["shared-peer", "shared-hidden", "shared-joined"][index]
        shared["origin"] = shared["origin"].replace(" 360 ", " 720 ")
        shared["visible"] = True if script is None else {
            "value": True, "script": "'use strict';\n" + script}
        shared_owners.append(shared)
    fixture["objects"].extend(shared_owners)
    fixture.pop("properties")
    fixture.update(description="Unregistered, identity-script and read-only observer sprites "
                               "share autoplay; hidden readers and joined owners resume the live phase.",
                   scenario="sprite-clock",
                   asset_files=["materials/selected/sprite0.tex"])
    return fixture
