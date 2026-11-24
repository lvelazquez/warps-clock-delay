// Host-side memory probe: member sizes/offsets of warps::Modulator.
// Build: see tests/run_probe.sh (uses `#define private public` to read offsets).
#include <cstdio>
#include <cstddef>
#define private public
#include "warps/dsp/modulator.h"
#undef private
using namespace warps;
#define M(name) std::printf("%-26s offset %7zu  size %7zu\n", #name, offsetof(Modulator, name), sizeof(((Modulator*)0)->name))
int main() {
  std::printf("sizeof(Modulator)=%zu  kOversampling=%d kMaxBlockSize=%zu\n",
              sizeof(Modulator), (int)kOversampling, kMaxBlockSize);
  M(xmod_oscillator_); M(vocoder_oscillator_); M(quadrature_oscillator_);
  M(src_up_); M(src_down_); M(vocoder_); M(quadrature_transform_); M(filter_);
  M(delay_buffer_); M(internal_modulation_); M(buffer_); M(src_buffer_);
  std::printf("DELAY_SIZE (frames) = %d  -> %.1f ms @96k, %.1f ms @48k\n",
              (int)Modulator::DELAY_SIZE, Modulator::DELAY_SIZE/96.0, Modulator::DELAY_SIZE/48.0);
  return 0;
}
