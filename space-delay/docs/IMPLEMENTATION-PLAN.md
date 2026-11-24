# Implementation plan and test plan

Source files that change (all under `upstream/symbiote/warps/`, on branch `space-delay`):

| File | Change |
|---|---|
| `dsp/parameters.h` | rename/repurpose `FEATURE_MODE_DUAL_FILTER` slot as Space Delay (keep enum order so saved settings stay valid) |
| `dsp/modulator.h/.cc` | `ProcessSpaceDelay`, member reorder so the ring overlays `vocoder_`, vocoder re-init on Meta entry (flag pattern of `reset_reverb`), dispatch at `modulator.cc:864` |
| `cv_scaler.h/.cc` | raw (unfiltered) Algorithm-CV accessor for the clock; mono-detect accessor |
| `ui.cc/.h` | flavor palette, secondary layer + pickup, `secondary_changed_` guard on release |
| `dsp/filters/dual_filter.h` | **kept**: the Ensemble mode uses `df` (`modulator.cc:428-444`). Not removed |

Not touched: bootloader, calibration data, stock Delay, Reverb, Ensemble, Doppler, Meta (behavior), stmlib (except the build patch).

## Phases (brief section 10), with entry gates

- **Phase 0 (this):** done: sources, baseline build + wav, memory audit, control map. Gate to Phase 1: decisions 1-4 in CONTROL-MAP.md answered.
- **Phase 1 (A1 Digital Hall only):** ring overlay + vocoder re-init, clock detector (host-tested first), anti-alias decimation, delay -> reverb.
  Gates: all other algorithms bit-identical to baseline on host renders; SRAM headroom not below the baseline's 1,088 B; hardware CPU measured with DWT.
- **Phase 2 (Bank A):** A2-A4 + bank/variation UI. **Phase 3 (Bank B)** only if Bank A passes CPU and stability. **Phase 4:** regression, soak.
- **Phase 5:** release candidate: wav, SHA256, install + recovery docs. Experimental builds stay in `builds/experimental/`.

## Test plan (host first; hardware items are listed for you to run)

Host harness (to build in `tests/`): compile `Modulator` for the host (the sizeof probe already compiles it), render WAVs for: silence, impulse,
sine, sweep, white noise, percussion, sustained synth, hot (full-scale) input, clock pulses with jitter, tempo ramps, dropouts.
Measure: delay time accuracy vs clock, clock acquisition time, reverb decay (RT60), idle noise floor, peak output and level consistency across flavors,
feedback stability at max, stereo correlation, click detection on division changes, bit-exactness of untouched algorithms against baseline.
**Host results are not hardware validation.**

Hardware acceptance checklist (you run it on the uWarps): module/MCU confirmed; baseline wav flashes and runs; CPU headroom via DWT build;
Hermod+ clock acquisition at 60/90/120/150 BPM, tempo change, clock stop/restart; every division audible and on grid; Meta mode after
leaving Space Delay (vocoder re-init); no output spike on mode switch; 1 h soak at max feedback; level match with bypass; mono vs stereo input.
