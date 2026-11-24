# Space Delay for Warps (work in progress)

A planned alternative mode for [Symbiote](https://github.com/leandrob13/eurorack) (the Warps firmware by leandrob13,
itself based on Mutable Instruments Warps and Parasites): a **clocked stereo delay feeding a reverb**, in the slot of the dual filter.

**Status: Phase 0. There is no Space Delay DSP code and no firmware to flash yet.** This branch holds the design, the memory audit
and the build tooling. The only source change against upstream `warps-v0.4.0` (257b43c) is a build fix in `warps/warps.cc`
(`__errno` as a function, for modern newlib).

## Planned features

- Delay time locked to an external clock on the Algorithm CV input, with the Algorithm knob choosing the division
  (1/16 to 2 bars; the longest ones are deliberately lo-fi and documented as such).
- Stereo in and out; a mono input is copied to both sides.
- Reverb after the delay, outside the feedback loop: Timbre sets the amount, Level 2 the decay, Level 1 the delay feedback.
- Two banks of four flavours, chosen with the button:
  - Bank A: Digital Hall, Tape Plate, Ping-Pong, Dual Room.
  - Bank B (only if Bank A meets CPU and stability targets): Reverse, Modulated, Diffused, Infinite.
- A longer delay line (about 300 ms stereo at full bandwidth) by reusing the memory of the Meta-mode vocoder.
- Click-free division changes (crossfaded taps) and an anti-alias filter before decimated writes.
- All other Symbiote modes left as upstream.

## Contents

| Path | What |
|---|---|
| `docs/DSP-ARCHITECTURE.md` | signal flow, clock detection, the eight flavours |
| `docs/CONTROL-MAP.md` | proposed controls and the four open design decisions |
| `docs/MEMORY-AUDIT.md` | RAM, CCM and flash budget of `warps-v0.4.0`, achievable divisions |
| `docs/IMPLEMENTATION-PLAN.md` | phases, files to change, test plan |
| `docs/RESEARCH.md`, `docs/INSTALLATION.md`, `docs/CHANGELOG.md` | background, flashing notes, history |
| `tools/build.sh` | builds Warps with a current Arm GNU Toolchain (set `ARM_TOOLCHAIN`) |
| `tools/encode_wav.py` | Python 3 port of the audio-bootloader `.wav` encoder |
| `tests/` | host probes for the size of `Modulator` |

The documents were written as working notes, so some refer to `builds/` and `references/` folders (baseline and upstream
release binaries) that are not published here, and `tools/build.sh` expects this repository checked out at `upstream/symbiote`
next to the `tools` folder.

The earlier clocked ping-pong delay, based on Symbiote 0.2.0, is on the
[`clock-delay`](https://github.com/lvelazquez/warps-clock-delay/tree/clock-delay) branch with a pre-release build.

Licences follow upstream: see the repository root.
