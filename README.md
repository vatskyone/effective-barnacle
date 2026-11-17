# WEB-1

**A portable synth, drum machine, sampler and 4-track tape recorder that runs in one web page.**

WEB-1 is a small instrument for making music in the browser. It has 16 synth engines, 8 drum kits, a sampler, sequencers, a master FX rack and a 4-track tape that you record on, loop, cut and play backwards. It is one HTML file with no install, no build step and no dependencies.

Designed and built by Snow Bayles, 2026.

### ▶ [Play WEB-1 in your browser](https://vatskyone.github.io/effective-barnacle/)

---

## Quick start

The fastest way is the **[live version](https://vatskyone.github.io/effective-barnacle/)**: open it, click the device and play. To run it on your own machine instead:

1. Download or clone this repository.
2. Open `index.html` in a recent desktop browser (Chrome, Edge, Firefox or Safari).
3. Click the device or press any key to switch the sound on.
4. Play notes with the **A W S E D F T G Y H U J K** keys, and press **/** for the controls card.

To serve it locally instead, for example to use MIDI or the microphone:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## What's inside

| Section | What it does |
|---|---|
| **Synth: bank A** (keys 1–8) | CLUSTER · FM · STRING · PULSE · ORGAN · FOLD · VOX · STORM |
| **Synth: bank B** (Shift + 1–8) | NEON · LADDER · ORBIT · SYNC · WAVES · AURORA · ACID · HOOVER: 80s and 90s synthwave, mono bass, poly brass, rave leads |
| **Drums** | 8 kits: BOX · DEEP · TINY · DIRT · TAPE · CLICK · AIR · ROOM |
| **Sampler** | Load, drop or record a sound into any synth slot and play it across the keys |
| **Tape** | 4 tracks × 60 s, overdub, loop, lift and drop, variable speed, reverse, brake and stutter tricks |
| **Sequencers** | ENDLESS · PATTERN · ARP |
| **FX** | A per-sound effect (ECHO · ROOM · CRUSH · SWIRL) plus a master rack (DRIVE → CHORUS → DELAY → REVERB) |
| **Mixer** | Level and pan per track, master EQ and drive, output, compressor and live-instrument level |
| **Timing** | Tempo, metronome, count-in, swing, live quantize, and bar and beat snapping |
| **Looks** | Light and dark case, and an OLED glow option for the screen |
| **MIDI** | Velocity, pitch bend, mod wheel and sustain from any connected keyboard |

Every sound has its own animated screen. The four coloured knobs always match the four coloured values on the screen.

Your sounds, sequences, samples and tape are saved automatically in your browser. **export tape as wav** downloads your mix.

## Guide

Read **[GUIDE.md](GUIDE.md)** for the full manual: every mode, key and knob, plus a first-song walkthrough.

## Technical notes

- Plain HTML, CSS and JavaScript in a single file: [`index.html`](index.html).
- Audio is the Web Audio API. Some engines and the tape run as AudioWorklets loaded from inline code.
- The screen is a canvas drawn at 3× resolution.
- Settings are saved in `localStorage`. The tape and samples are saved in IndexedDB.
- Nothing is sent anywhere: everything runs and stays on your machine.

## Browser support

WEB-1 works best in a recent Chromium-based browser (Chrome, Edge, Arc, Brave). Firefox and Safari work too. Web MIDI needs Chrome or Edge, and the microphone needs `localhost` or HTTPS. It is built for a desktop keyboard; touch and mouse also work on the on-screen keys.

## Credits

Design, sounds and code: Snow Bayles, 2026. WEB-1 is an original instrument and is not affiliated with any hardware maker.
