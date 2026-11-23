#!/usr/bin/env bash
set -euo pipefail
cq_project_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cq_capture_dir="${1:-$cq_project_dir/verification/captures}"
cq_renderer="${2:-forward_plus}"
cq_resolution="${3:-1920x1080}"
mkdir -p -- "$cq_capture_dir"
exec godot --path "$cq_project_dir" --audio-driver Dummy --rendering-method "$cq_renderer" --resolution 1280x720 --log-file "$cq_capture_dir/godot_capture.log" -- --capture "--capture-dir=$cq_capture_dir" "--capture-size=$cq_resolution"
