# Memory audit (baseline = unmodified `warps-v0.4.0` @ 257b43c)

Sources: linker map `builds/original/warps.map`, `nm -S`, `tests/sizeof_probe.cc` (host layout; differs from ARM by 536 B total).
CPU cost is **not measured** (no hardware): see "What is unmeasured".

## Totals

| Region | Capacity | Used | Free |
|---|---|---|---|
| Flash (app) | 1,015,808 B | 123,456 B (12.2%) | ~892 KB |
| SRAM | 131,072 B | `.data` 208 + `.bss` 129,776 = 129,984 | **1,088 B, and `_Min_Stack_Size` is 1,024 -> 64 B headroom** |
| CCM | 65,536 B | `reverb_buffer` 65,536 (100%) | 0 |

Stack and ISRs live in the 1,088 B below `_estack` (0x20020000). Heap size is 0.

## SRAM owners

| Object | Bytes |
|---|---|
| `modulator` (one static object) | 122,808 |
| `codec` | 6,284 |
| everything else (UI, settings, statics) | ~684 |

Inside `Modulator` (host layout, indicative):

| Member | Bytes | Note |
|---|---|---|
| `vocoder_` | **65,760** (53.5%) | used only by Meta mode (`modulator.cc:327-329`) |
| `delay_buffer_` | 49,152 (12,288 stereo frames) | |
| `src_buffer_` / `buffer_` / `internal_modulation_` | 4,608 / 1,152 / 384 | scratch for every algorithm |
| quadrature transform, oscillators, SRC, filters | ~1,900 | |

The "delay line" is `delay_buffer_` **plus the scratch members that follow it** (`DELAY_SIZE` = 13,821 frames = 144 ms @ 96 kHz).
The standalone Delay and Doppler algorithms can use the scratch area because they do not need it; **a mode that also runs the reverb on
`buffer_[0..2]` cannot**, so a combined mode is limited to 12,288 frames (128 ms) unless the ring moves.

## CCM (reverb buffer)

`Reverb` is one Griesinger/Dattorro topology in `FxEngine<32768, FORMAT_16_BIT>` using 21,617 words; the four `ReverbType`s
(Caveman/Rings/Clouds/Elements) differ in parameter mapping, not memory. `Ensemble` initializes on the **same** buffer
(1,022 words), so Reverb and Ensemble cannot run together; Reverb and the SRAM delay can. Free words: 11,151 (22 KB), usable
only if Ensemble is not active.

## Answers to the Phase 0 questions

1. **Does removing the filters free RAM?** No: ~48 B RAM, ~2.4 KB flash. It only frees a mode slot.
2. **Can delay and reverb run simultaneously?** Yes, memory-wise: delay is SRAM, reverb is CCM, independent. Constraint: ring <= 12,288 frames unless relocated.
3. **Biggest lever:** overlay the delay ring on `vocoder_` (65,760 B, Meta-only). Needs member reordering so the ring is contiguous and a vocoder re-init
   when returning to Meta (pattern exists: `reset_reverb`, `modulator.cc:857`). Ring becomes 28,886 stereo frames (301 ms) or 57,772 mono samples (602 ms).
4. **Aliasing:** the existing variable-rate write (used for decimating long delays) interpolates but applies **no anti-alias filter** on the
   written signal (the filters in `ProcessDelay`, `modulator.cc` analog state, shape the feedback for tone only), so long delays alias bright sources.
   Verified by reading `ProcessDelay` in 0.4.0; the audible effect is not measured yet. Any decimated mode needs an anti-alias low-pass before the write.

## Achievable clock divisions (bandwidth of stored signal, Nyquist = 24 kHz x rate)

120 BPM, quarter-note clock:

| Division | Time | Stereo 12,288 fr (stock) | Stereo 28,886 fr (overlay) | Mono 57,772 (overlay) |
|---|---|---|---|---|
| 1/16 | 125 ms | 24.0 kHz | 24.0 | 24.0 |
| 1/8 | 250 ms | 12.3 | 24.0 | 24.0 |
| dotted 1/8 | 375 ms | 8.2 | 19.3 | 24.0 |
| 1/4 | 500 ms | 6.1 | 14.4 | 24.0 |
| dotted 1/4 | 750 ms | 4.1 | 9.6 | 19.3 |
| 1/2 | 1.0 s | 3.1 | 7.2 | 14.4 |
| 1 bar | 2.0 s | 1.5 | 3.6 | 7.2 |
| 2 bars | 4.0 s | 0.8 | 1.8 | 3.6 |

The brief's full list (1/32 ... two bars) is **not** achievable at clean quality on the stock layout; with the overlay, 1/16 .. dotted 1/4 are clean
(stereo) and 1 bar / 2 bars are deliberately lo-fi. These must be documented, never silently offered (brief section 6).

## What is unmeasured

- CPU cycles per block for any mode (needs DWT cycle counter on hardware). Budget: 105,000 cycles/block.
- Stack high-water mark (needs hardware or an emulator; 64 B headroom above the minimum is the static fact).
- Idle noise, headroom, reverb decay: host harness not yet built (TEST-PLAN in IMPLEMENTATION-PLAN.md).
