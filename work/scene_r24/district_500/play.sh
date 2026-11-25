#!/usr/bin/env bash
set -euo pipefail
directory="$(cd "$(dirname "$0")" && pwd)"
root="$(git -C "$directory" rev-parse --show-toplevel)"
project="$root/work/project/chongqing_godot_v05"
engine="${GODOT_BIN:-$root/.cloud-dev/tools/bin/godot}"
if [[ ! -x "$engine" ]]; then
    engine="$(command -v godot || true)"
fi
if [[ -z "$engine" || "$("$engine" --version)" != 4.6.3.* ]]; then
    echo "Set GODOT_BIN to the Godot 4.6.3 executable." >&2
    exit 1
fi
if [[ "${1:-}" == "--software" ]]; then
    shift
    export LIBGL_ALWAYS_SOFTWARE=1
    exec "$engine" --path "$project" --rendering-method gl_compatibility --resolution 960x540 "$@"
fi
exec "$engine" --path "$project" "$@"
