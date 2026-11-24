# Space Delay: DSP architecture (proposal, not implemented)

Replaces the filter slot (position 1, `FEATURE_MODE_DUAL_FILTER`, `modulator.cc:864`). All other modes, including the stock
Delay at position 8 with its four button states, are left as upstream.

## Signal flow

```
in1 (L) --+                                       +--> delay taps (L,R) --+
          +--> input gain --> [mono detect] -->   |                        +--> dry/wet mix --> out
in2 (R) --+                    (in2 unpatched    delay ring + feedback      |        ^
                               => R = L)         (tone filter, soft safety) |        |
                                                      |                     |   reverb send
                                                      +--> reverb (outside the feedback loop) --+
```

- **Reverb outside the feedback loop** (default). Reverb send = delay repeats + a fixed fraction of the dry input per flavor
  (so both "delay then reverb" and "reverberated echoes" are reachable). Reverb tail keeps ringing when input is muted because the
  reverb is not gated by input.
- **Memory:** delay ring in SRAM (overlay on `vocoder_`, see MEMORY-AUDIT.md section "Answers" #3), reverb in CCM. The scratch arrays
  (`buffer_`, `src_buffer_`, `internal_modulation_`) stay outside the ring because the reverb stage runs on them.
- **Reuse, don't duplicate:** one engine (`ProcessSpaceDelay`) with a per-flavor parameter struct. Existing `Reverb` is used as is
  (`reverb.h`; freeze is `ELEMENTS`-only, see B4). The decimated-write path from `ProcessDelay` is reused but gets an anti-alias low-pass in front.

## Clock

- Source: **Algorithm CV, raw ADC value** (new accessor in `CvScaler`; the existing path low-passes it at 0.08/block). Sampled once per
  60-frame block (~1.6 kHz): edge timing +/-0.6 ms; at 120 BPM that is 0.12% period error before smoothing.
- Detection: rising edge with hysteresis (thresholds to be fixed from measured ADC values, not guessed), min gap to reject bounce,
  period = median of the last few edges with outlier rejection; retains last tempo when the clock stops (free-run at that tempo; default 120 BPM).
- Quarter-note pulses assumed. Division set (clean vs lo-fi is documented in MEMORY-AUDIT.md): 1/16, 1/8T, 1/8, dotted 1/8, 1/4, dotted 1/4, 1/2, 1 bar, 2 bars.
  Divisions the ring can't hold cleanly are **flagged lo-fi**, not hidden.
- **Why not audio input 2 as the clock** (what the earlier prototype did): audio timing is better (96 kHz), but it costs the right channel. Space Delay is stereo,
  so the clock goes on a CV. Trade-off to confirm: Algorithm CV is no longer available for division modulation.

## Division changes

Digital flavors crossfade two read taps (old time -> new time over ~20-50 ms) so a change is click-free and pitch-stable. Tape Plate (A2) intentionally
slews the time (pitch sweep). The stock Delay's single 0.5 s slew is **not** reused for digital flavors, because in the capped regime it does not slew at all and
the rate smoother (1.5 ms) produces a pitch step instead (analysis of the earlier prototype, `modulator.cc:614-622` in the 0.2.0 tree).

## Flavors (distinct on purpose; Bank A first)

| | Delay character | Reverb character | Resource notes |
|---|---|---|---|
| A1 Digital Hall | clean stereo taps, Hermite read | neutral, long | baseline |
| A2 Tape Plate | LP/HP in loop, LFO wow/flutter, soft saturation (the only place saturation is intended) | plate: bright, dense | +1 LFO |
| A3 Ping-Pong | crossfed L/R feedback (carried from the earlier prototype, incl. bipolar tone) | wide, diffuse | none |
| A4 Dual Room | two related taps (e.g. 1/8 and dotted 1/8) | short, defined | second read tap |
| B1 Reverse | reverse read, two overlapping windows | atmospheric | second read tap, window LUT |
| B2 Modulated | chorus/detune on taps | reverb LFOs raised | +2 LFOs |
| B3 Diffused | allpass smear in loop, increasing per repeat | merges into wash | allpass in loop (small RAM) |
| B4 Infinite | feedback ceiling with limiter | `ELEMENTS` reverb type: freeze exists only there, engaged when reverb time >= 0.95 (`reverb.h:209`), input gain forced to 0 (`reverb.h:191`); B4 must use that type or add its own freeze | stability test mandatory |

Bank B is **Phase 3 and conditional** on Bank A meeting CPU and stability targets (brief priority 5 vs 6).

## Audio-quality rules

- Fixed headroom: input scaled to leave >= 6 dB before the ring; no saturation to hide gain staging (only A2, by design).
- Feedback cap per flavor with a worst-case sum check (dry + repeats + reverb); the stock delay's `1.1x` feedback multiplier is **not** used.
- Parameter changes interpolate per sample (pattern in `ProcessDelay`); denormals flushed in loop filters; DC blocked at the loop input.
- Anti-alias low-pass before any decimated write; measured on host before any claim.
