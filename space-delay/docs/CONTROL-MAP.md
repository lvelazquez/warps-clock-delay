# Space Delay: control map (proposed; needs your sign-off, see "Decisions")

Gestures that **exist today** and are reused unchanged (`ui.cc`):

| Gesture | Existing meaning |
|---|---|
| Hold button + move Algorithm knob | select mode (pickup via `kAlgoChangeThreshold`) |
| Hold button + move Timbre across 0.5 | `alt_feature_mode_` (bank). Only the filter slot reads it today, so Space Delay can own it |
| Short press | cycle `carrier_shape_` 0..3 (variation) |
| Hold ~7.8 s | calibration. Untouched |

## Primary (Space Delay active)

| Control | Function | Notes |
|---|---|---|
| Algorithm knob | clock division (quantized with hysteresis) | free in normal operation, no mode-lock needed |
| Timbre knob | reverb amount | |
| Level 1 | delay feedback | |
| Level 2 | reverb decay | |
| Button (short) | next variation in the active bank (A1..A4 or B1..B4) | |
| Hold + Timbre across 0.5 | bank A / B | existing gesture; osc LEDs already show `!alt` / `alt` while held |
| Algorithm CV | **external clock** (raw ADC) | division has no CV |
| Timbre CV | reverb amount mod | |
| Level 1 / 2 CV | feedback / decay mod | existing normalization behavior (0.6 when unpatched) must be accounted for |
| In 1 / In 2 | L / R; **in 2 unpatched -> R = L** | `DetectAudioNormalization` (`cv_scaler.cc:98`) zeroes an unpatched input, so mono detect is a cheap check |
| Out / Aux | L / R | |

## Secondary layer: **conflict**, needs a decision

The brief puts secondary controls "behind a button hold". Hold already means mode select (Algorithm) and bank (Timbre), so on the Algorithm and
Timbre knobs it cannot carry a second layer. What is free while held: **Level 1 and Level 2** (the feature-switch code only reads Algorithm and Timbre pots).

| Option | Reachable secondary params | Cost |
|---|---|---|
| **A (recommended)** | hold + Level 1 = delay wet/dry, hold + Level 2 = input gain; reverb brightness/damping and manual delay time are fixed per flavor | needs a `secondary_changed_` flag so a hold-and-twist does not also cycle the variation on release; pickup per knob |
| B | all four brief secondary params via a new double-tap/long-tap gesture | new gesture design and testing; conflicts with the 7.8 s calibration hold if timed carelessly |

Pickup (both): on entering hold, store each pot's position; a secondary value changes only after its pot moves past a threshold
(same technique as `kAlgoChangeThreshold`), so entering/leaving the layer never jumps a parameter.

## LEDs

- Main LED color: flavor palette (replaces the filter-slot colors in `feature_mode_palette_`, `ui.cc:58`).
- Osc LEDs: variation (existing 2-bit pattern); while held they show the bank (existing).
- Clock activity: a short main-LED pulse on each detected edge is possible; proposed as optional (brief section 5), prove it doesn't disturb the palette first.

## Decisions I need from you

1. Secondary layer: option A or B?
2. Clock on **Algorithm CV** (stereo kept, no division CV) vs audio In 2 (mono-only effect)?
3. Overlay the delay ring on the vocoder memory (Meta mode then re-initializes its vocoder on entry; first block after returning to Meta may cost extra CPU)?
4. Confirm your exact module and MCU (the build here targets STM32F4 at 168 MHz).
