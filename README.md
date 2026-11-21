# WEB-1

**A portable synth, drum machine, sampler and 4-track tape recorder that runs in one web page.**

WEB-1 is a small instrument for making music in the browser. It has 24 synth engines that can go in any of its 16 sound slots, 8 drum kits (with your own samples on any pad), a drum machine with a 16-step pattern, a sampler, sequencers, 8 sound effects, a master FX rack and a 4-track tape that you record on, loop, cut and play backwards. It is one HTML file with no install, no build step and no dependencies.

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
| **Synth: bank A** (keys 1–8, named A1–A8) | CLUSTER · FM · STRINGS · PULSE · ORGAN · FOLD · HERO · STORM |
| **Engine library** (white knob in the synths & presets menu) | Any engine in any slot, plus eight more: PLUCK (plucked string), TINE (electric piano), BOOM (deep sub bass that glides), MALLET (marimba, vibes, glass, kalimba), GRAIN (granular clouds), VOWEL (choir and talking pads), CHIP (8-bit with arpeggios) and FELT (soft piano), each with its own presets and animated screen. Every sound can play POLY, MONO, LEGATO or UNISON with glide, drift and velocity (Shift + T2) |
| **Synth: bank B** (Shift + 1–8 in synth mode) | NEON · LADDER · ORBIT · VELVET · BRASS · AURORA · ACID · HOOVER: 80s and 90s synthwave, mono bass, analog pads, poly brass, rave leads |
| **Key & chords** (Shift + TEMPO) | Lock the keys to one of 11 scales so every note fits, and play whole chords from one key (triads, sevenths, ninths built from the scale, plus sus, power and octave shapes), with voicings, strum, an added bass note and scale dots on the keys |
| **Synths & presets menu** (Shift + SYNTH) | Every synth in one list with INIT plus 4 presets each; browse with the knobs and play while you browse. Save your own presets with Shift + T1, name them with the knobs or the keyboard, and delete them again. The orange knob makes a random sound |
| **Drums** | 8 kits: BOX · DEEP · TINY · DIRT · TAPE · CLICK · AIR · ROOM, with your own sample on any pad, trimmed, tuned, reversed, faded and played as one shot, gated or looped in the pad sample editor (Shift + 4), with a playhead that follows each hit. Each kit can switch between four sound models: CLASSIC, ANALOG (classic analog drum machine), PUNCH and DUSTY (lo-fi), and the closed hat chokes the open hat |
| **Drum machine** (Shift + DRUM) | 12 pads built from 2 synth voices and a filter each, 8 patterns of 16 steps that chain together, and per-step velocity, chance, rolls and nudge, plus a hits generator for quick rhythms |
| **Sampler** | Load, drop or record a sound into any synth slot and play it across the keys, as one shot, gated or looped, forwards or reversed, with fades and a playhead that follows each note, on the same screen and knobs as the drum pad editor |
| **Tape** | 4 tracks × 60 s with big turning reels, bar lines, an FX box that turns orange while effects are on, advanced recording (Shift + REC: mic or instrument, overdub or replace, start on sound or on the next bar, auto stop, punch), erase-all by holding T1–T4 together (Shift + TAPE), overdub, loop, lift and drop, copy, crop, double and erase (Shift + T1–T4), variable speed, reverse, brake and stutter tricks |
| **Sequencers** | ENDLESS · PATTERN · ARP · CHAIN (an endless step sequencer with chords, long notes and rests) |
| **FX** | 8 per-sound effects (ECHO · ROOM · CRUSH · SWIRL, plus BOUNCE · COIL · CUBE · RADIO on Shift + T3) and a master rack with two banks: DRIVE → CHORUS → DELAY → REVERB, and FILTER → GATE → FLANGER → LO-FI on Shift + FX. Each of the 8 per-sound effects has its own animated screen with its two main values in big numbers |
| **Mixer** | Mute and solo on keys 1–8, four scenes that store and glide between whole mixes (Shift + 1–8), reverb and delay sends per track, a sidechain that makes the tracks pump with the drums, bouncing tracks together, and export as a tape mix, stems or a live mixdown (Shift + MIXER). Level and pan per track on one page, a 3-band multiband compressor, a 4-band EQ with movable frequencies, and a master page with compressor, stereo width and a limiter. Shift + knobs reach the extra settings on every page |
| **System menu** (Shift + 8 in tape mode) | Battery, time and timezone, storage (erase samples, presets, the tape or everything), display brightness and sleep, and about. Built now to try out the hardware version's settings |
| **Timing** | Tempo, metronome, count-in, swing, live quantize, and bar and beat snapping |
| **Looks** | Aluminium-style case with keys set in a thin black grid, a frameless screen with full-screen animated pictures, light or dark finish, a flat line-art finish, and a subtle OLED glow option. The REC key is a red disc set inside its ring |
| **MIDI** | Velocity, pitch bend, mod wheel and sustain from any connected keyboard; MIDI clock out and in, and notes out from the sequencers or everything you play (system menu) |

Synths are named A1–A8 and B1–B8 on the screen and in the menu. Every sound has its own animated screen, drawn to fill the display: a vintage string-machine panel for STRINGS, an arcade space shooter for HERO, swirling saw waves for HOOVER, a retro android with an LED visor for VELVET, a line-art vintage polysynth for BRASS, a synthwave sunset for NEON and aurora curtains for AURORA (both in the four flat knob colours), and more. The four coloured knobs always match the four coloured values on the screen.

On the desktop, WEB-1 is drawn as a piece of hardware: every key, knob panel and keyboard key sits on a black plate, so a thin black line runs between and around the controls. Keys have large rings with bold icons and numbers that all line up, the knobs sit in rings, the black keys' row has no gaps and sits on clean black lines, and the speaker is a round grille. The SYNTH, DRUM, FX and number keys light orange when their second layer (menu, drum machine, FX bank B, synth bank B) is in use. The screen is set flush into that grid with no bezel, fills its whole tile, and stays a black display in every finish. "by Snow Bayles - 2026" is engraved into the case beside the WEB-1 name, and the controls card opens from the **guide** button under the device.

Your sounds, sequences, samples and tape are saved automatically in your browser as **projects**: keep several songs, open, duplicate and rename them, and save any of them (or a backup of all of them) to a **.web1 file** to keep or move to another computer. **Shift + DROP** undoes the last change to the tape. The system menu shows how much space your work uses and can erase it. **export tape as wav** downloads your mix.

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
