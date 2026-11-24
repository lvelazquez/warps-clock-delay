# Research and baseline (Phase 0)

Status: **host-side and build-only.** Nothing here has run on hardware.

## 1. What we are building on

| Item | Value | How verified |
|---|---|---|
| Repo | `leandrob13/eurorack` (Symbiote fork of MI `eurorack`) | `gh api repos/leandrob13/eurorack` |
| Default branch `master` | Warps **0.2.0** state (what I first cloned and prototyped on) | modes in `parameters.h` match the 0.2.0 post |
| Latest Warps branch | `warps-v0.4.0`, tip `257b43c` (2024-04-06) = tag `v0.4.0-beta` + 3 commits | `git describe` = `v0.4.0-beta-3-g257b43c` |
| Other Warps branches | `warps-v0.3.0`, `warps-v0.3.1` | `gh api .../branches` |
| stmlib (pinned submodule) | `e3bd7c9` | `git submodule status` |
| stm_audio_bootloader (pinned) | `b376bd6` | `git submodule status` |
| Local clone | `upstream/symbiote`, blobless partial clone (history intact), sparse on `warps/`, branch `space-delay` | |
| Local commits on top of upstream | 1: `build: Define __errno as a function for modern newlib` | `git log` |

**The earlier 0.2.0-era clocked-delay prototype is not on this base.** It was written against `master`. It is
not carried over; the clocked delay is re-implemented fresh as a Space Delay variation (see DSP-ARCHITECTURE.md).

## 2. Brief vs source (discrepancies)

| Brief / assumption | Source says | Evidence |
|---|---|---|
| 0.4.0-beta has consolidated stereo + parallel filter banks | **True**, but as one slot (position 1, `FEATURE_MODE_DUAL_FILTER`) with one binary flag choosing `STEREO_FILTER` vs `DUAL_FILTER` | `modulator.cc:864-866` |
| "Two banks x four variations" interface exists | **True** in this form: bank = `alt_feature_mode_` (hold button + Timbre past 0.5), variation = `carrier_shape_` (button short-press, 4 values) | `ui.cc:208`, `modulator.cc:865` |
| Removing filter banks frees meaningful RAM | **No.** `DualFilter` is 48 B of RAM and ~2.4 KB of flash (416+1168+768 B). `FilterBank` belongs to the vocoder | `nm -S`, host `sizeof` probe |
| Doppler panner may need restoring | **Already present** at position 7 in 0.4.0 (`FEATURE_MODE_DOPPLER`). Nothing to restore unless we remove it | `parameters.h:44-54` |
| Algorithm knob can be clock division without leaving the mode | **True.** Algorithm select is hold-button + Algorithm knob with pickup (`kAlgoChangeThreshold`=0.01); in normal operation the knob is free. No mode-lock needed | `ui.cc:85,184-198` |
| Secondary controls via button-hold | **Conflicts** with existing hold gestures (hold+Algorithm = mode select, hold+Timbre = bank). Proposal in CONTROL-MAP.md | `ui.cc` |
| Algorithm CV can carry a clock | **Possible but not as-is.** CVs are sampled once per 60-frame block (~1.6 kHz) and the Algorithm CV is low-passed (0.08/block). A clock must read the raw ADC value | `cv_scaler.cc:127,139`, `warps.cc:109` |
| Existing clock detection can be reused | **None exists** in 0.4.0 (grep for clock/tempo/edge finds nothing relevant) | source |

## 3. Hardware and platform (from the firmware, not from the module)

- Target: STM32F4xx, `F_CPU` 168 MHz, 8 MHz crystal, linker `STM32F4xx_1024K_192K`:
  application flash from `0x08008000` (1M-32K), RAM 128K, CCM 64K (`warps/makefile`, `stmlib/linker_scripts/stm32f4xx_flash_application_large.ld`).
- Audio: **96 kHz**, **60-frame blocks** (`warps.cc:47,109`) -> 105,000 CPU cycles per block, **1,750 cycles per frame**.
- **UNVERIFIED:** that your uWarps uses the same MCU/memory map. Symbiote's post says it targets Warps clones in
  general. Confirm the exact module/MCU before flashing anything (see IMPLEMENTATION-PLAN.md, open decisions).

## 4. Licensing

- MI code and stmlib are MIT-licensed (file headers). The Symbiote repo has **no LICENSE file** (GitHub API: `license: null`);
  the blog's CC BY-NC-SA applies to the blog text only. Personal use is fine; **ask the author before redistributing** a derived build.
- Keep MI and Symbiote attribution headers intact.

## 5. Toolchain (reproducible)

- Arm GNU Toolchain 15.3.rel2, installed at `~/.local/arm-gnu-toolchain` (path must contain no spaces; stmlib's makefile does not quote it).
  The brew cask failed (its pkg needs sudo); the cached pkg was unpacked with `pkgutil --expand-full` instead.
- `tools/build.sh [outdir]` builds with `-std=gnu++11 -Wno-error` (vendored CMSIS trips GCC 15 under `-Werror`) and applies
  `tools/patches/stmlib-discard-exidx.sh` (discards `.ARM.exidx/.ARM.extab`, which overlap `.data` otherwise).
- Baseline artifact: `builds/original/` (`warps.bin` sha256 `aa106372...`). One vendored-code warning (CMSIS `sp` clobber), none from Warps code.
- `.wav` encoder: upstream is **Python 2**. `tools/encode_wav.py` is a Python 3 port. Validated by re-encoding the released
  `v0.4.0-beta` hex and comparing with the released wav: same length (6,143,232 samples), every sample within **1 LSB**
  (8.5% differ by +/-1, from float rounding). Not byte-identical; equivalent for a QPSK demodulator. Hardware has not confirmed it.
