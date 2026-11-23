#!/usr/bin/env bash
# Set up an agent workspace for Task 2 (evidence-backed fix) without a container.
#
# Usage: bash env/setup_env.sh <target_dir>
#
# Copies starter/ into <target_dir> and creates <target_dir>/.agent-bin/ with
# `python` and `python3`, which run uv-managed CPython 3.12.14 from a virtual
# environment under .agent-bin/envs/ with pytest 8.3.5 installed. The commands
# are small wrapper scripts that exec the virtual-environment interpreter.
# Prints the PATH line an agent harness should use. Needs uv on PATH.
set -euo pipefail

PY="3.12.14"
PYTEST="pytest==8.3.5"

[ $# -eq 1 ] || { echo "usage: bash setup_env.sh <target_dir>" >&2; exit 2; }
command -v uv >/dev/null || { echo "uv is required (brew install uv)" >&2; exit 2; }

HERE="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$1"
if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "target directory exists and is not empty: $TARGET" >&2; exit 2
fi
mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
cp -R "$HERE/starter/." "$TARGET/"

BIN="$TARGET/.agent-bin"
ENV_DIR="$BIN/envs/py312"
mkdir -p "$BIN/envs"
export UV_PYTHON_PREFERENCE=only-managed
uv venv --quiet --python "$PY" "$ENV_DIR"
uv pip install --quiet --python "$ENV_DIR/bin/python" "$PYTEST"
for name in python python3; do
  printf '#!/bin/sh\nexec "%s" "$@"\n' "$ENV_DIR/bin/python" > "$BIN/$name"
  chmod +x "$BIN/$name"
done

echo "Workspace ready: $TARGET"
echo "PATH line for the agent harness:"
echo "export PATH=\"$BIN:\$PATH\""
