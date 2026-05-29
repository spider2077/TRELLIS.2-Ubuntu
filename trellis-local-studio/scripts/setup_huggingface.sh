#!/usr/bin/env bash
# Script: setup_huggingface.sh
# Location: trellis-local-studio/scripts/setup_huggingface.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_ROOT"

CHECK_ONLY=false
DOWNLOAD=false

usage() {
  cat <<'EOF'
Usage: ./scripts/setup_huggingface.sh [OPTIONS]

Options:
  --check       Verify Hugging Face login and required model access only.
  --download    After auth checks pass, pre-download TRELLIS.2 dependencies.
  -h, --help    Show this help.

TRELLIS.2 requires Hugging Face access to:
  - microsoft/TRELLIS.2-4B
  - facebook/dinov3-vitl16-pretrain-lvd1689m (gated — accept license on the model page)
  - briaai/RMBG-2.0 (gated — accept license on the model page)

Setup:
  1. Open each gated model page and request access:
     https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m
     https://huggingface.co/briaai/RMBG-2.0
  2. Create a read token at https://huggingface.co/settings/tokens
  3. Run: hf auth login
     or: HF_TOKEN=your_token hf auth login --token "$HF_TOKEN"
  4. Run: ./scripts/setup_huggingface.sh --check
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      CHECK_ONLY=true
      shift
      ;;
    --download)
      DOWNLOAD=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

CONDA_SH=""
for candidate in \
  "$HOME/miniforge3/etc/profile.d/conda.sh" \
  "$HOME/miniconda3/etc/profile.d/conda.sh" \
  "$HOME/anaconda3/etc/profile.d/conda.sh"; do
  if [ -f "$candidate" ]; then
    CONDA_SH="$candidate"
    break
  fi
done

if [ -n "$CONDA_SH" ]; then
  # shellcheck disable=SC1090
  . "$CONDA_SH"
  if [ "${CONDA_DEFAULT_ENV:-}" != "trellis2" ]; then
    conda activate trellis2
  fi
fi

if ! command -v hf >/dev/null 2>&1; then
  echo "Error: hf CLI not found. Activate the trellis2 environment first."
  exit 1
fi

echo "== Hugging Face setup for Trellis Local Studio =="
echo

if [ "${HF_TOKEN:-}" != "" ]; then
  echo "Logging in with HF_TOKEN..."
  hf auth login --token "$HF_TOKEN"
elif ! hf auth whoami >/dev/null 2>&1; then
  echo "You are not logged in to Hugging Face."
  echo
  echo "Before logging in, request access to:"
  echo "  https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m"
  echo "  https://huggingface.co/briaai/RMBG-2.0"
  echo
  echo "Then run:"
  echo "  hf auth login"
  echo
  if [ "$CHECK_ONLY" = false ]; then
    hf auth login
  else
    exit 1
  fi
fi

python - <<'PY'
from app.utils.huggingface_auth import check_huggingface_auth, format_huggingface_setup_help

status = check_huggingface_auth()
if status.username:
    print(f"Logged in as: {status.username}")
else:
    print("Not logged in to Hugging Face.")

print()
for repo in status.repos:
    state = "OK" if repo.get("accessible") else "BLOCKED"
    print(f"[{state}] {repo['repo_id']}")
    if repo.get("gated"):
        print(f"       access page: {repo['access_url']}")
    if repo.get("error"):
        print(f"       note: {repo['error']}")

if not status.ready:
    print()
    print(format_huggingface_setup_help())
    raise SystemExit(1)

print()
print("Hugging Face auth checks passed.")
PY

if [ "$DOWNLOAD" = true ]; then
  echo
  echo "Pre-downloading models..."
  python scripts/download_model.py
fi

if [ "$CHECK_ONLY" = true ]; then
  echo "Check complete."
fi
