"""Direct sound creation and its retained configuration and control state."""

import io
import math
import struct
import wave


def make_fixture():
    audio = io.BytesIO()
    with wave.open(audio, "wb") as output:
        output.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
        output.writeframes(b"".join(struct.pack("<hh", sample, -sample) for sample in
            (round(1800 * math.sin(2 * math.pi * 440 * frame / 48000))
             for frame in range(48000))))
    script = """'use strict';
const asset = engine.registerAsset('sounds/tone.wav');
export function init(value) {
    const inputs = ['sounds/tone.wav', asset, {sound:'sounds/tone.wav'},
                    {sound:['sounds/tone.wav']}];
    const passed = [];
    for (let i = 0; i < inputs.length; ++i) {
        const layer = thisScene.createLayer(inputs[i]);
        let valid = false;
        if (layer) {
            const config = thisScene.getInitialLayerConfig(layer);
            const expected = i === 3 ? ['sounds/tone.wav'] : 'sounds/tone.wav';
            valid = JSON.stringify(config.sound) === JSON.stringify(expected) &&
                    Object.keys(config).sort().join(',') === 'id,sound' &&
                    layer.volume === 1 && layer.isPlaying();
            layer.stop();
            valid = valid && !layer.isPlaying();
            layer.volume = 0.25;
            layer.play();
            valid = valid && layer.volume === 0.25 && layer.isPlaying();
        }
        passed.push(valid);
        console.log('DirectSoundFixture', i, valid);
    }
    // Keep the array control involved in all three output channels. These pixels observe
    // creation and requested playback state; separate PCM captures verify decoder output.
    return new Vec3(passed[0] && passed[3] ? 0.25 : 0,
                    passed[1] && passed[3] ? 0.5 : 0,
                    passed[2] && passed[3] ? 0.75 : 0);
}
"""
    prefix = "INFO SceneScript log: DirectSoundFixture"
    return {
        "description": "Sound paths, registered assets and scalar/array configurations retain defaults and playback controls.",
        "docs": ["scene/scenescript/reference/class/IScene.md",
                 "scene/scenescript/reference/class/IAssetHandle.md",
                 "scene/scenescript/reference/class/ISoundLayer.md"],
        "general": {"clearcolor": {"value": "0 0 0", "script": script}},
        "files": {"sounds/tone.wav": audio.getvalue()},
        "log_expectations": {prefix: [f"{prefix} {i} true" for i in range(4)]},
    }
