# Installation and recovery (Phase 0 state: nothing flashed, nothing automated)

I have **not** flashed anything and will not. Firmware updates are audio-based (the QPSK `.wav`). Do not use any of these on hardware
until the module/MCU is confirmed (CONTROL-MAP.md, decision 4).

## Artifacts

| File | What |
|---|---|
| `builds/original/warps-v0.4.0+3-baseline.wav` | unmodified upstream `warps-v0.4.0` @ 257b43c, modern toolchain, **built here, not hardware-tested** |
| `builds/original/warps.bin`, `.hex`, `.elf`, `.map`, `SHA256SUMS` | same build |
| `references/release-v0.4.0-beta/warps-v0-4-0-beta.wav` | the author's released beta, the safest **known-good** firmware to keep for rollback |

`SHA256SUMS`: `warps.bin` aa10637243477620e1e60040cb757bc53455454620dbff4f6133d2a4d8e7edd3,
baseline wav fc54fb24a1627a97a45c9904eb80a2187a1fad83009e416ded6a94b293115bc5.

## Update procedure

Use the module's own audio update procedure from the official manual
(https://pichenettes.github.io/mutable-instruments-documentation/modules/warps/manual/, per Symbiote's page); I have not
verified the steps for your clone, so check them against your module's documentation first.

## Recovery

- The bootloader (first 32 KB, application at `0x08008000`) is never modified by these builds, so a bad application can be re-flashed over audio.
- Roll back by re-flashing the **released** `warps-v0-4-0-beta.wav` (known good for other users) before trying our baseline.
- If the update never starts, the failure is the module/procedure, not the firmware; stop and report before trying anything else.
