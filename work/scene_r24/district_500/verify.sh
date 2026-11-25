#!/usr/bin/env bash
set -euo pipefail
directory="$(cd "$(dirname "$0")" && pwd)"
: "${GODOT_BIN:?Set GODOT_BIN to the Godot 4.6.3 executable}"
: "${CQ_QA_DIR:?Set CQ_QA_DIR to a fresh absolute directory}"
project="$directory/../../project/chongqing_godot_v05"
run="$CQ_QA_DIR"
if [[ -e "$run" ]]; then
    echo "Use a fresh evidence directory." >&2
    exit 1
fi
mkdir -p "$run/sections" "$run/routes" "$run/first_shift" "$run/user-data"
export XDG_DATA_HOME="$run/user-data"
headless=("$GODOT_BIN" --headless --fixed-fps 60 --path "$project")
"${headless[@]}" --quit-after 180 >"$run/default.log" 2>&1
"${headless[@]}" --quit-after 180 -- --explore-500 >"$run/explore.log" 2>&1
CQ_QA_DIR="$run/sections" "${headless[@]}" --script "$directory/probe.gd" -- --day-one-test >"$run/sections/engine.log" 2>&1
CQ_QA_DIR="$run/routes" "${headless[@]}" --script "$directory/routes.gd" -- --district-500-test >"$run/routes/engine.log" 2>&1
"${headless[@]}" --script "$directory/../indoor_delivery/verify_shift.gd" -- --day-one-test "--qa-dir=$run/first_shift" >"$run/first_shift/engine.log" 2>&1
if rg -n '^(SCRIPT ERROR|SHADER ERROR|ERROR):' "$run" --glob '*.log'; then
    exit 1
fi
