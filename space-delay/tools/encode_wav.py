#!/usr/bin/env python3
"""Python 3 port of stm_audio_bootloader's QPSK encoder (stm32f4 target).

Upstream (pichenettes/stm-audio-bootloader, pinned at b376bd6) is Python 2.
This port keeps the arithmetic identical: every Python 2 integer `/` became
`//`, and byte handling uses `bytes`. It is validated by encoding a released
firmware .hex and comparing against the released .wav (see docs/INSTALLATION.md).

usage: encode_wav.py firmware.bin [-o out.wav]   (defaults match Warps:
       -t stm32f4 -s 48000 -b 12000 -c 6000 -p 256)
"""
import argparse
import struct
import sys
import zlib

import numpy

STM32F4_SECTOR_BASE_ADDRESS = [
    0x08000000, 0x08004000, 0x08008000, 0x0800C000, 0x08010000, 0x08020000,
    0x08040000, 0x08060000, 0x08080000, 0x080A0000, 0x080C0000, 0x080E0000,
]
STM32F4_BLOCK_SIZE = 16384
STM32F4_APPLICATION_START = 0x08008000


class WavWriter:
    """Mono 16-bit PCM writer (port of audio_stream_writer.AudioStreamWriter)."""

    def __init__(self, path, sample_rate, bitdepth=16, channels=1):
        self._sample_rate = sample_rate
        self._bitdepth = bitdepth
        self._channels = channels
        self._f = open(path, 'wb')
        self._num_bytes = 0
        self._write_header(False)

    @staticmethod
    def quantize(signal, bitdepth):
        scaled = signal.copy()
        if numpy.abs(scaled).max() > 1.0:
            scaled[scaled < -1] = -1
            scaled[scaled > 1] = 1
        scale = (1 << (bitdepth - 1)) - 1
        scaled = scaled * scale
        return numpy.array(scaled, dtype='i%d' % (bitdepth // 8))

    def _write_header(self, restore_position):
        f = self._f
        total_size = 4 + 8 + 16 + 8 + self._num_bytes
        position = f.tell()
        f.seek(0)
        f.write(b'RIFF')
        f.write(struct.pack('<L', total_size))
        f.write(b'WAVEfmt ')
        byte_rate = self._sample_rate * self._channels * (self._bitdepth // 8)
        block_align = self._channels * (self._bitdepth // 8)
        f.write(struct.pack('<LHHLLHH', 16, 1, self._channels,
                            self._sample_rate, byte_rate, block_align,
                            self._bitdepth))
        f.write(b'data')
        f.write(struct.pack('<L', self._num_bytes))
        if restore_position:
            f.seek(position)

    def append(self, signal):
        if signal.dtype == numpy.int16:
            scaled = signal
        else:
            scaled = self.quantize(signal, self._bitdepth)
        scaled.tofile(self._f)
        self._num_bytes += scaled.nbytes
        self._write_header(True)

    def close(self):
        self._f.close()


class QpskEncoder:
    def __init__(self, sample_rate=48000, carrier_frequency=2000,
                 bit_rate=8000, packet_size=256):
        period = sample_rate // carrier_frequency
        symbol_time = sample_rate // (bit_rate // 2)
        assert (symbol_time % period == 0) or (period % symbol_time == 0)
        assert (sample_rate % carrier_frequency) == 0
        assert (sample_rate % bit_rate) == 0
        self._sr = sample_rate
        self._br = bit_rate
        self._carrier_frequency = carrier_frequency
        self._sample_index = 0
        self._packet_size = packet_size

    @staticmethod
    def _upsample(x, factor):
        return numpy.tile(x.reshape(len(x), 1), (1, factor)).ravel()

    def _encode_qpsk(self, symbol_stream):
        ratio = self._sr // self._br * 2
        symbol_stream = numpy.array(symbol_stream)
        even = 2 * self._upsample(symbol_stream % 2, ratio) - 1
        odd = 2 * self._upsample(symbol_stream // 2, ratio) - 1
        return even / numpy.sqrt(2.0), odd / numpy.sqrt(2.0)

    def _modulate(self, q_mod, i_mod):
        num_samples = len(q_mod)
        t = (numpy.arange(0.0, num_samples) + self._sample_index) / self._sr
        self._sample_index += num_samples
        phase = 2 * numpy.pi * self._carrier_frequency * t
        return q_mod * numpy.sin(phase) + i_mod * numpy.cos(phase)

    def _encode(self, symbol_stream):
        return self._modulate(*self._encode_qpsk(symbol_stream))

    def _code_blank(self, duration):
        num_zeros = int(duration * self._br / 8) * 4
        return self._encode(numpy.zeros(num_zeros, dtype=int))

    def _code_packet(self, data):
        assert len(data) <= self._packet_size
        if len(data) != self._packet_size:
            data = data + b'\xff' * (self._packet_size - len(data))
        crc = zlib.crc32(data) & 0xffffffff
        preamble = [0] * 8 + [0x99] * 4 + [0xcc] * 4
        crc_bytes = [crc >> 24, (crc >> 16) & 0xff, (crc >> 8) & 0xff,
                     crc & 0xff]
        stream = preamble + list(data) + crc_bytes
        symbols = []
        for byte in stream:
            symbols.append((byte >> 6) & 0x3)
            symbols.append((byte >> 4) & 0x3)
            symbols.append((byte >> 2) & 0x3)
            symbols.append((byte >> 0) & 0x3)
        return self._encode(symbols)

    def code_intro(self):
        yield numpy.zeros(1 * self._sr)
        yield self._code_blank(1.0)

    def code_outro(self, duration=1.0):
        yield self._code_blank(duration)

    def code(self, data, page_size=1024, blank_duration=0.06):
        if len(data) % page_size != 0:
            data += b'\xff' * (page_size - (len(data) % page_size))
        offset = 0
        remaining = len(data)
        written = 0
        while remaining:
            size = min(remaining, self._packet_size)
            yield self._code_packet(data[offset:offset + size])
            written += 1
            if written == page_size // self._packet_size:
                yield self._code_blank(blank_duration)
                written = 0
            remaining -= size
            offset += size


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('firmware')
    ap.add_argument('-o', '--output')
    ap.add_argument('-s', '--sample-rate', type=int, default=48000)
    ap.add_argument('-c', '--carrier', type=int, default=6000)
    ap.add_argument('-b', '--baud', type=int, default=12000)
    ap.add_argument('-p', '--packet-size', type=int, default=256)
    args = ap.parse_args()

    data = open(args.firmware, 'rb').read()
    out = args.output or (args.firmware[:-4] + '.wav'
                          if args.firmware.endswith('.bin')
                          else args.firmware + '.wav')

    enc = QpskEncoder(args.sample_rate, args.carrier, args.baud,
                      args.packet_size)
    w = WavWriter(out, args.sample_rate, 16, 1)
    for block in enc.code_intro():
        w.append(block)
    for x in range(0, len(data), STM32F4_BLOCK_SIZE):
        address = STM32F4_APPLICATION_START + x
        pause = 3.5 if address in STM32F4_SECTOR_BASE_ADDRESS else 0.2
        for block in enc.code(data[x:x + STM32F4_BLOCK_SIZE],
                              STM32F4_BLOCK_SIZE, pause):
            if len(block):
                w.append(block)
    for block in enc.code_outro(5.0):
        w.append(block)
    w.close()
    print('wrote', out, file=sys.stderr)


if __name__ == '__main__':
    main()
