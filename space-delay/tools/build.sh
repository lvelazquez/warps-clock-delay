#!/bin/sh
# Build a Warps firmware from upstream/symbiote with the bundled toolchain.
# usage: tools/build.sh [outdir]   (default builds/experimental)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/upstream/symbiote"
# stmlib's makefile uses the toolchain path unquoted, so it must contain no spaces.
TC="${ARM_TOOLCHAIN:-$HOME/.local/arm-gnu-toolchain}"
OUT="${1:-$ROOT/builds/experimental}"
case "$OUT" in /*) ;; *) OUT="$PWD/$OUT" ;; esac
sh "$ROOT/tools/patches/stmlib-discard-exidx.sh" "$SRC"
cd "$SRC"
rm -rf build
# -std=gnu++11 / -Wno-error: vendored CMSIS uses 'register' and deprecated asm
# clobbers that modern GCC rejects under the makefile's -Werror.
make -f warps/makefile TOOLCHAIN_PATH="$TC/" \
  CPPFLAGS="-fno-exceptions -fno-rtti -std=gnu++11 -Wno-error" -j8 \
  > "$OUT.build.log" 2>&1 || { tail -30 "$OUT.build.log"; exit 1; }
mkdir -p "$OUT"
cp build/warps/warps.hex build/warps/warps.elf build/warps/warps.map "$OUT"/
"$TC/bin/arm-none-eabi-objcopy" -O binary build/warps/warps.elf "$OUT/warps.bin"
"$TC/bin/arm-none-eabi-size" build/warps/warps.elf | tee "$OUT/size.txt"
