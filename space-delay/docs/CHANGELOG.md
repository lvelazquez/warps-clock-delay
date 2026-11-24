# Changelog

## Phase 0 (2026-11-23)

- Re-based from `master` (0.2.0) to `warps-v0.4.0` @ 257b43c; real history via blobless partial clone.
- Baseline `warps-v0.4.0` builds with Arm GNU Toolchain 15.3 (`tools/build.sh`); one tracked change on `space-delay`:
  `__errno` as a function. Build-only patch for stmlib's linker script in `tools/patches/`.
- Python 3 `.wav` encoder port (`tools/encode_wav.py`), validated against the released beta within 1 LSB.
- Memory audit, control map, DSP architecture, plan. No DSP changes yet.
- The earlier 0.2.0-based clocked-delay prototype (in `../symbiote-eurorack`) is superseded and not carried over.
