Warps clock delay
=================

A fork of [leandrob13/eurorack](https://github.com/leandrob13/eurorack) (the Symbiote firmwares, themselves built on [Parasites](https://github.com/mqtthiqs/parasites) and the original Mutable Instruments code) that changes one thing in the Warps firmware: the first variant of the delay mode becomes a **clocked ping-pong delay**.

In the delay mode, with the internal oscillator button in its first state (off):

* **Input 2** takes a clock instead of audio. The delay follows the measured clock period; without a clock it starts at 120 BPM, and if the clock stops it holds the last tempo.
* **Algorithm** picks the delay time as a ratio of the clock period: 1/4, 1/3, 1/2, 2/3, 3/4, 1, 1.5, 2, 3, 4. When a time does not fit the delay buffer, the write sample rate drops so that it still fits.
* **Timbre** is a tone control on the repeats: left of noon low-pass, noon flat, right of noon high-pass. The filter sits in the feedback path, so every repeat is filtered again.
* **Level 1** is the feedback and **Level 2** the dry/wet mix, as before.
* The two outputs carry the dry input 1 mixed with the left and right sides of the ping-pong.

This replaces the "open feedback loop" variant of that button state. The other two button states of the delay mode and every other mode are unchanged.

Installing
----------

The [releases](../../releases) carry `warps.wav` for the audio bootloader (the usual Mutable Instruments firmware update procedure) and `warps.hex` / `warps.bin` for a programmer. Install at your own risk.

Building
--------

```
git submodule update --init stmlib stm_audio_bootloader
make -f warps/makefile TOOLCHAIN_PATH=/path/to/arm-gnu-toolchain/ bin
```

It builds with a current Arm GNU Toolchain (15.3 was used). For that, `warps/makefile` uses its own copy of the linker script (`warps/linker/`), compiles as C++11 without treating warnings as errors, and `stmlib` is pinned to a newer commit. `make -f warps/makefile wav` needs Python 2, like upstream.

The changes are in `warps/dsp/modulator.cc` (`Modulator::ProcessDelay`). Same licence as upstream: MIT for the STM32 code.

The original README follows.

Mutable Instruments' Eurorack Modules.

* [Beads](http://mutable-instruments.net/modules/beads): Texture synthesizer (1).
* [Blades](http://mutable-instruments.net/modules/blades): Dual multimode filter.
* [Blinds](http://mutable-instruments.net/modules/blinds): Quad VC-polarizer.
* [Braids](http://mutable-instruments.net/modules/braids): Macro-oscillator.
* [Branches](http://mutable-instruments.net/modules/branches): Dual Bernoulli gate.
* [Clouds](http://mutable-instruments.net/modules/clouds): Texture synthesizer.
* [Ears](http://mutable-instruments.net/modules/ears): Contact microphone.
* [Edges](http://mutable-instruments.net/modules/edges): Quad chiptune digital oscillator.
* [Elements](http://mutable-instruments.net/modules/elements): Modal synthesizer.
* [Frames](http://mutable-instruments.net/modules/frames): Keyframer/mixer.
* [Grids](http://mutable-instruments.net/modules/grids): Topographic drum sequencer.
* [Kinks](http://mutable-instruments.net/modules/kinks): Utility module - rectifier, analog logic, S&H, noise.
* [Links](http://mutable-instruments.net/modules/links): Utility module - buffer, mixer.
* [Marbles](http://mutable-instruments.net/modules/marbles): Random sampler.
* [Peaks](http://mutable-instruments.net/modules/peaks): Dual trigger converter.
* [Plaits](http://mutable-instruments.net/modules/plaits): Macro oscillator.
* [Rings](http://mutable-instruments.net/modules/rings): Resonator.
* [Ripples](http://mutable-instruments.net/modules/ripples): Liquid 2-pole BP, 2-pole LP and 4-pole LP filter.
* [Shades](http://mutable-instruments.net/modules/shades): Triple attenuverter.
* [Shelves](http://mutable-instruments.net/modules/shelves): EQ filter.
* [Stages](http://mutable-instruments.net/modules/stages): Segment generator.
* [Streams](http://mutable-instruments.net/modules/streams): Dual dynamics gate.
* [Tides](http://mutable-instruments.net/modules/tides): Tidal modulator.
* [Veils](http://mutable-instruments.net/modules/veils): Quad VCA.
* [Volts](http://mutable-instruments.net/modules/volts): +5V power module.
* [Warps](http://mutable-instruments.net/modules/warps): Meta-modulator.
* [Yarns](http://mutable-instruments.net/modules/yarns): MIDI interface.

(1) Code provided as is, builds on a Desktop platform but not verified to build and run on a module. Install at your own risks.

License
=======

Code (AVR projects): GPL3.0.

Code (STM32F projects): MIT license.

Hardware: cc-by-sa-3.0

By: Emilie Gillet (emilie.o.gillet@gmail.com)

Guidelines for derivative works
===============================

**Mutable Instruments is a registered trademark.**

The name "Mutable Instruments" should not be used on any of the derivative works you create from these files.

We do not recommend you to keep the original name of the Mutable Instruments module for your derivative works.

For example, your 5U adaptation of Mutable Instruments Clouds can be called "Foobar Modular - Particle Generator".
