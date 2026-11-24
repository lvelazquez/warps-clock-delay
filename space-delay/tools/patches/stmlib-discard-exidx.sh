#!/bin/sh
# Idempotently discard .ARM.exidx/.ARM.extab in the vendored stmlib linker
# script. Newlib/libgcc unwind tables otherwise overlap .data in flash on
# modern toolchains; the firmware is built with -fno-exceptions.
set -e
LD="$1/stmlib/linker_scripts/stm32f4xx_flash_application_large.ld"
grep -q 'ARM.exidx' "$LD" && exit 0
python3 - "$LD" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
s=s.replace("  DISCARD :\n","  /DISCARD/ :\n  {\n    *(.ARM.exidx*)\n    *(.ARM.extab*)\n  }\n\n  DISCARD :\n",1)
open(p,'w').write(s)
PY
