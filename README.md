# WEB-1

**A portable synth, drum machine, sampler and 4-track tape recorder that runs in one web page.**

WEB-1 is a small instrument for making music in the browser. It has 16 synth engines, 8 drum kits (with your own samples on any pad), a drum machine with a 16-step pattern, a sampler, sequencers, 8 sound effects, a master FX rack and a 4-track tape that you record on, loop, cut and play backwards. It is one HTML file with no install, no build step and no dependencies.

Designed and built by Snow Bayles, 2026.

### ▶ [Play WEB-1 in your browser](https://vatskyone.github.io/effective-barnacle/)

---

## Quick start

The fastest way is the **[live version](https://vatskyone.github.io/effective-barnacle/)**: open it, click the device and play. To run it on your own machine instead:

1. Download or clone this repository.
2. Open `index.html` in a recent desktop browser (Chrome, Edge, Firefox or Safari).
3. Click the device or press any key to switch the sound on.
4. Play notes with the **A W S E D F T G Y H U J K** keys, and press **/** (or click **guide**) for the controls card.

To serve it locally instead, for example to use MIDI or the microphone:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## OS-1: the iPhone version

Open the same link on an iPhone and WEB-1 becomes **OS-1**: the same instrument re-laid out for touch in landscape, sized to fill the phone's screen: the display and the four knobs on top, two rows of keys, and two octaves along the bottom. Hold the phone sideways (with rotation lock on it still fills the screen, drawn turned).

- Tap **?** on the device for the controls card and the tools (export, samples, dark mode, OLED, line art, reset).
- Drag the knobs up or down; double-tap one to reset it. Hold **shift** with one finger and tap with another.
- For full screen, tap Share in Safari and choose **Add to Home Screen**. OS-1 then opens like an app.
- If you hear nothing, turn the volume up and switch silent mode off.

OS-1 switches on by itself on touch phones. Add `?os1` to the address to try it in a desktop browser, or `?web1` to get the desktop device on a phone. It shares its saved sounds and tape with WEB-1 in the same browser.

## What's inside

| Section | What it does |
|---|---|
| **Synth: bank A** (keys 1–8, named A1–A8) | CLUSTER · FM · STRING · PULSE · ORGAN · FOLD · HERO · STORM |
| **Synth: bank B** (Shift + 1–8 in synth mode) | NEON · LADDER · ORBIT · VELVET · BRASS · AURORA · ACID · HOOVER: 80s and 90s synthwave, mono bass, analog pads, poly brass, rave leads |
| **Synths & presets menu** (Shift + SYNTH) | Every synth in one list with INIT plus 4 presets each; browse with the knobs and play while you browse |
| **Drums** | 8 kits: BOX · DEEP · TINY · DIRT · TAPE · CLICK · AIR · ROOM, with your own sample on any pad, trimmed, tuned or reversed in the pad sample editor (Shift + 4) |
| **Drum machine** (Shift + DRUM) | 12 pads built from 2 synth voices and a filter each, plus a 16-step pattern |
| **Sampler** | Load, drop or record a sound into any synth slot and play it across the keys |
| **Tape** | 4 tracks × 60 s, overdub, loop, lift and drop, copy, crop, double and erase (Shift + T1–T4), variable speed, reverse, brake and stutter tricks |
| **Sequencers** | ENDLESS · PATTERN · ARP · CHAIN (an endless step sequencer with chords, long notes and rests) |
| **FX** | 8 per-sound effects (ECHO · ROOM · CRUSH · SWIRL, plus BOUNCE · COIL · CUBE · RADIO on Shift + T3) and a master rack with two banks: DRIVE → CHORUS → DELAY → REVERB, and FILTER → GATE → FLANGER → LO-FI on Shift + FX |
| **Mixer** | Level and pan per track on one page, a 3-band multiband compressor, a 4-band EQ with movable frequencies, and a master page with compressor, stereo width and a limiter. Shift + knobs reach the extra settings on every page |
| **Timing** | Tempo, metronome, count-in, swing, live quantize, and bar and beat snapping |
| **Looks** | Aluminium-style case with keys set in a thin black grid, a frameless screen with full-screen animated pictures, light or dark finish, a flat line-art finish, and a subtle OLED glow option |
| **MIDI** | Velocity, pitch bend, mod wheel and sustain from any connected keyboard |

Every sound has its own animated screen, drawn to fill the display: an arcade space shooter for HERO, a retro android with an LED visor for VELVET, a line-art vintage polysynth for BRASS, a synthwave sunset for NEON, and more. The four coloured knobs always match the four coloured values on the screen.

On the desktop, WEB-1 is drawn as a piece of hardware: every key, knob panel and keyboard key sits on a black plate, so a thin black line runs between and around the controls. Keys have large rings with bold icons and numbers that all line up, the knobs sit in rings, the black keys' row has no gaps and sits on clean black lines, and the speaker is a round grille. The SYNTH, DRUM, FX and number keys light orange when their second layer (menu, drum machine, FX bank B, synth bank B) is in use. The screen is set flush into that grid with no bezel, fills its whole tile, and stays a black display in every finish. "by Snow Bayles - 2026" is engraved into the case beside the WEB-1 name, and the controls card opens from the **guide** button under the device.

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

WEB-1 works best in a recent Chromium-based browser (Chrome, Edge, Arc, Brave). Firefox and Safari work too. Web MIDI needs Chrome or Edge, and the microphone needs `localhost` or HTTPS. The desktop device is built for a computer keyboard; on a phone it turns into OS-1, the touch layout (a recent iOS and Safari recommended).

## Credits

Design, sounds and code: Snow Bayles, 2026. WEB-1 is an original instrument and is not affiliated with any hardware maker.
