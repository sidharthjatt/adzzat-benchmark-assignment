#!/usr/bin/env bash
# Set up an agent workspace for Task 1 (pinned runtime) without a container.
#
# Usage: bash env/setup_env.sh <target_dir>
#
# Copies starter/ into <target_dir> and creates <target_dir>/.agent-bin/ with:
#   python, python3 -> uv-managed CPython 3.12.14 (the default the agent sees)
#   python3.9       -> uv-managed CPython 3.9.25 (the project's stated target)
# Each interpreter is a virtual environment under .agent-bin/envs/ with
# pytest 8.3.5 installed. The commands in .agent-bin/ are small wrapper
# scripts that exec the matching virtual-environment interpreter.
# Prints the PATH line an agent harness should use. Needs uv on PATH.
set -euo pipefail

PY_DEFAULT="3.12.14"
PY_TARGET="3.9.25"
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
mkdir -p "$BIN/envs"
export UV_PYTHON_PREFERENCE=only-managed

make_env() {  # make_env <name> <version>
  local env="$BIN/envs/$1"
  uv venv --quiet --python "$2" "$env"
  uv pip install --quiet --python "$env/bin/python" "$PYTEST"
  echo "$env/bin/python"
}

wrapper() {  # wrapper <command name> <interpreter path>
  printf '#!/bin/sh\nexec "%s" "$@"\n' "$2" > "$BIN/$1"
  chmod +x "$BIN/$1"
}

PY312="$(make_env py312 "$PY_DEFAULT")"
PY39="$(make_env py39 "$PY_TARGET")"
wrapper python "$PY312"
wrapper python3 "$PY312"
wrapper python3.9 "$PY39"

echo "Workspace ready: $TARGET"
echo "PATH line for the agent harness:"
echo "export PATH=\"$BIN:\$PATH\""
