#!/usr/bin/env bash
# Use the same engines and entry points as district_patrol/verify.ps1 on Linux.
set -euo pipefail
repo=/workspace/chongqing-refresh
project="$repo/work/project/chongqing_godot_v05"
scene="$repo/work/scene_r24/district_patrol"
godot=/workspace/work/runtime/.cloud-dev/tools/bin/godot
xvfb=/workspace/work/runtime/district-refresh/houci-77-2SHdvmUw/xvfb-package/usr/bin
run="$1"
phase="$2"
[[ -d "$run" && "$run" == /* ]]
export PATH="$xvfb:$PATH" LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=3
export XDG_CACHE_HOME=/workspace/work/runtime/cache
cd "$repo"
case_run() {
    local label="$1" relative="$2" method="$3" rc=0
    shift 3
    local dest="$run/$label"
    mkdir "$dest" "$dest/data" "$dest/config"
    export CQ_QA_DIR="$dest" XDG_DATA_HOME="$dest/data" XDG_CONFIG_HOME="$dest/config"
    local draw=(--headless --fixed-fps 60) go=() game=(--day-one-test --qa-still-frames)
    case "$method" in
        native) go=("$xvfb/xvfb-run" -a -s '-screen 0 1280x760x24 -nolisten tcp'); draw=(--rendering-method gl_compatibility --resolution 1000x564 --disable-vsync --disable-render-loop --fixed-fps 60);;
        timing) go=("$xvfb/xvfb-run" -a -s '-screen 0 1280x760x24 -nolisten tcp'); draw=(--rendering-method gl_compatibility --resolution 1152x648 --disable-vsync); game=(--day-one-test);;
    esac
    if [[ "$method" != headless ]]; then game+=(--qa-no-sun-shadows); fi
    local invocation=("${go[@]}" "$godot" "${draw[@]}" --audio-driver Dummy --path "$project"
        --log-file "$dest/engine.log" --script "$scene/$relative" -- "${game[@]}" "--qa-dir=$dest" "$@")
    printf '%q ' "${invocation[@]}" > "$dest/command.txt"
    timeout --kill-after=15 660 "${invocation[@]}" > "$dest/console.log" 2>&1 || rc=$?
    printf '%s\n' "$rc" > "$dest/exit-code.txt"
    if [[ -r "$dest/engine.log" ]]; then rg -n '^(SCRIPT ERROR|SHADER ERROR|ERROR):' "$dest/engine.log" > "$dest/engine-errors.txt" || true; fi
    printf '%s %s\n' "$label" "$rc"
}
case "$phase" in
    physical|bench-and-state)
        case_run pavement pavement.gd headless
        case_run sections ../vertical_run/section.gd headless
        case_run teaching ../indoor_delivery/verify_shift.gd headless
        case_run counter ../vertical_run/reopen.gd headless "--from=$run/teaching/completed.cfg" --counter
        case_run single ../indoor_delivery/free_order.gd headless "--checkpoints=$run/teaching"
        case_run lunch ../lunch_run/verify.gd headless --practice-lunch
        case_run market ../outer_neighborhood/market_entry.gd headless --explore-500 --outer-market
        case_run repair ../repair_court/walk.gd headless --explore-500 --repair-court
        case_run shancheng ../street_blocks/handoff.gd headless --explore-500 --shancheng
        [[ "$phase" == bench-and-state ]] && exit 0
        ;;&
    physical|all-road-physics)
        case_run ground ../district_age/audit.gd headless
        for direction in out back; do
            options=()
            [[ "$direction" == back ]] && options+=(--reverse)
            for batch in 0 1 2; do
                case_run "player_${direction}_${batch}" ../district_age/drive_matrix.gd headless "--batch=$batch" "${options[@]}"
            done
        done
        ;;
    visual)
        case_run north entry_corner/north.gd native
        case_run ride patrol.gd native
        case_run turns junctions.gd native
        case_run older_crossings legacy_views.gd native --practice-passage
        case_run junction_profiles entry_corner/verify.gd native --practice-passage
        case_run sites sites.gd native --practice-passage
        case_run home local_route.gd native --practice-passage
        case_run bridge ../vertical_run/verify.gd native --practice-passage
        case_run restore ../vertical_run/reopen.gd headless "--from=$run/bridge/bridge.cfg"
        case_run timing ../vertical_run/timing.gd timing --practice-passage
        ;;
    *) exit 2;;
esac
