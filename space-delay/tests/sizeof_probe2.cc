#include <cstdio>
#include "warps/dsp/modulator.h"
using namespace warps;
int main(){ std::printf("sizeof Reverb=%zu DualFilter=%zu Ensemble=%zu Vocoder=%zu FxEngine-based Reverb buffer is external\n", sizeof(Reverb), sizeof(DualFilter), sizeof(Ensemble), sizeof(Vocoder)); }
