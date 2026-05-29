#!/usr/bin/env bash
# Script: prepare_cuda_glibc_patch.sh
# Location: trellis-local-studio/scripts/prepare_cuda_glibc_patch.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEM_CUDA_HOME="${SYSTEM_CUDA_HOME:-${CUDA_HOME:-/usr/local/cuda-12.4}}"
PATCH_ROOT="${TRELLIS_CUDA_PATCH_ROOT:-$HOME/.local/share/trellis-local-studio/shadow-cuda}"
SRC_HEADER="$SYSTEM_CUDA_HOME/include/crt/math_functions.h"
PATCH_HEADER="$PATCH_ROOT/include/crt/math_functions.h"

if [ ! -f "$SRC_HEADER" ]; then
  echo "Error: CUDA math header not found at $SRC_HEADER"
  exit 1
fi

mkdir -p "$PATCH_ROOT/include/crt"

if [ ! -f "$PATCH_HEADER" ] || [ "$SRC_HEADER" -nt "$PATCH_HEADER" ]; then
  echo "Preparing patched CUDA math header for glibc 2.41+ compatibility..."
  cp "$SRC_HEADER" "$PATCH_HEADER"
  sed -i \
    -e 's/double                 rsqrt(double x);/double                 rsqrt(double x) noexcept(true);/' \
    -e 's/float                  rsqrtf(float x);/float                  rsqrtf(float x) noexcept(true);/' \
    -e 's/double                 sinpi(double x);/double                 sinpi(double x) noexcept(true);/' \
    -e 's/float                  sinpif(float x);/float                  sinpif(float x) noexcept(true);/' \
    -e 's/double                 cospi(double x);/double                 cospi(double x) noexcept(true);/' \
    -e 's/float                  cospif(float x);/float                  cospif(float x) noexcept(true);/' \
    -e 's/__func__(double rsqrt(double a));/__func__(double rsqrt(double a)) throw();/' \
    -e 's/__func__(double sinpi(double a));/__func__(double sinpi(double a)) throw();/' \
    -e 's/__func__(double cospi(double a));/__func__(double cospi(double a)) throw();/' \
    -e 's/__func__(float rsqrtf(float a));/__func__(float rsqrtf(float a)) throw();/' \
    -e 's/__func__(float sinpif(float a));/__func__(float sinpif(float a)) throw();/' \
    -e 's/__func__(float cospif(float a));/__func__(float cospif(float a)) throw();/' \
    "$PATCH_HEADER"
  echo "Patched header written to: $PATCH_HEADER"
else
  echo "Using existing patched CUDA header: $PATCH_HEADER"
fi

link_or_copy() {
  local src="$1"
  local dst="$2"
  if [ -e "$dst" ]; then
    return 0
  fi
  mkdir -p "$(dirname "$dst")"
  if ln -s "$src" "$dst" 2>/dev/null; then
    return 0
  fi
  if [ -d "$src" ]; then
    cp -a "$src" "$dst"
  else
    cp -a "$src" "$dst"
  fi
}

for rel in bin lib64 nvvm targets extras; do
  if [ -e "$SYSTEM_CUDA_HOME/$rel" ]; then
    link_or_copy "$SYSTEM_CUDA_HOME/$rel" "$PATCH_ROOT/$rel"
  fi
done

mkdir -p "$PATCH_ROOT/include"
for entry in "$SYSTEM_CUDA_HOME/include"/*; do
  base="$(basename "$entry")"
  if [ "$base" = "crt" ]; then
    continue
  fi
  link_or_copy "$entry" "$PATCH_ROOT/include/$base"
done

mkdir -p "$PATCH_ROOT/include/crt"
for entry in "$SYSTEM_CUDA_HOME/include/crt"/*; do
  base="$(basename "$entry")"
  if [ "$base" = "math_functions.h" ]; then
    continue
  fi
  link_or_copy "$entry" "$PATCH_ROOT/include/crt/$base"
done

export CUDA_HOME="$PATCH_ROOT"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export TRELLIS_CUDA_PATCH_ROOT="$PATCH_ROOT"
export NVCC_PREPEND_FLAGS="${NVCC_PREPEND_FLAGS:--allow-unsupported-compiler}"

echo "Using shadow CUDA_HOME for builds: $CUDA_HOME"
