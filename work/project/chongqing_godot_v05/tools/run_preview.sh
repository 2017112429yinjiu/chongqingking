#!/usr/bin/env bash
set -euo pipefail
cq_project_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cq_renderer="${1:-forward_plus}"
exec godot --path "$cq_project_dir" --audio-driver Dummy --rendering-method "$cq_renderer" --resolution 1600x900
