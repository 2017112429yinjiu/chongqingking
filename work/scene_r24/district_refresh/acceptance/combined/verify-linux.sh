#!/usr/bin/env bash
# Native Linux counterpart to district_patrol/verify.ps1 -AllRoads -Timing.
set -euo pipefail
base="$(cd "$(dirname "$0")" && pwd)"
repo="$(git -C "$base" rev-parse --show-toplevel)"
project="$repo/work/project/chongqing_godot_v05"
scene="$repo/work/scene_r24/district_patrol"
run="$(realpath -m "$1")"
phase="${2:-all}"
godot="${GODOT_BIN:-godot}"
xvfb="${XVFB_RUN:-xvfb-run}"
blender="${BLENDER_BIN:-blender}"
[[ "$("$godot" --version)" == 4.6.3.* ]]
export LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS="${LP_NUM_THREADS:-3}"
concurrency="${CQ_R24_CONCURRENCY:-1}"
visual_limit="${CQ_R24_VISUAL_LIMIT:-660}"
timing_limit="${CQ_R24_TIMING_LIMIT:-660}"
mkdir -p "$run"
cd "$repo"

case_run() {
    local label="$1" relative="$2" method="$3" rc=0 limit="$visual_limit"
    shift 3
    local dest="$run/$label"
    if [[ "${CQ_R24_RESUME:-0}" = 1 && -f "$dest/exit-code.txt" ]]; then
        return
    fi
    mkdir "$dest"
    mkdir "$dest/data" "$dest/config"
    local lease=''
    if [[ -n "${CQ_GODOT_LOCK_PATH:-}" ]]; then
        exec {lease}>"$CQ_GODOT_LOCK_PATH"
        flock "$lease"
    fi
    local -a draw=(--headless --fixed-fps 60) go=() gameplay=(--day-one-test --qa-still-frames)
    case "$method" in
        native)
            go=("$xvfb" -a -s '-screen 0 1280x760x24 -nolisten tcp')
            draw=(--rendering-method gl_compatibility --resolution 1000x564 --position 40,40
                  --disable-vsync --disable-render-loop --fixed-fps 60)
            gameplay+=(--qa-no-sun-shadows)
            ;;
        software-timing)
            go=("$xvfb" -a -s '-screen 0 1280x760x24 -nolisten tcp')
            draw=(--rendering-method gl_compatibility --resolution 1152x648 --disable-vsync --disable-render-loop)
            gameplay=(--day-one-test --qa-no-sun-shadows)
            limit=1200
            ;;
        timing)
            go=("$xvfb" -a -s '-screen 0 1280x760x24 -nolisten tcp')
            draw=(--rendering-method gl_compatibility --resolution 1152x648 --disable-vsync)
            gameplay=(--day-one-test --qa-no-sun-shadows)
            limit="$timing_limit"
            ;;
    esac
    if [[ "$method" != headless && -n "${CQ_R24_SHADER_ROOT:-}" ]]; then
        local project_name
        project_name=$(sed -n 's/^config\/name="\(.*\)"$/\1/p' "$project/project.godot" | head -1)
        if [[ -n "$project_name" ]]; then
            local user_path="$dest/data/godot/app_userdata/$project_name"
            mkdir -p "$user_path" "$CQ_R24_SHADER_ROOT"
            ln -s "$CQ_R24_SHADER_ROOT" "$user_path/shader_cache"
        fi
    fi
    local -a invocation=("${go[@]}" "$godot" "${draw[@]}" --audio-driver Dummy --path "$project"
        --log-file "$dest/engine.log" --script "$scene/$relative" -- "${gameplay[@]}" "--qa-dir=$dest" "$@")
    printf '%q ' "${invocation[@]}" > "$dest/command.txt"
    CQ_QA_DIR="$dest" XDG_DATA_HOME="$dest/data" XDG_CONFIG_HOME="$dest/config" \
        timeout --kill-after=15 "$limit" "${invocation[@]}" > "$dest/console.log" 2>&1 || rc=$?
    printf '%s\n' "$rc" > "$dest/exit-code.txt"
    if [[ -r "$dest/engine.log" ]]; then
        rg -n '^(SCRIPT ERROR|SHADER ERROR|ERROR):' "$dest/engine.log" > "$dest/engine-errors.txt" || true
    fi
    if [[ -n "$lease" ]]; then
        exec {lease}>&-
    fi
    printf '%s %s\n' "$label" "$rc"
}

state() {
    case_run pavement pavement.gd headless
    case_run sections ../vertical_run/section.gd headless
    case_run teaching ../indoor_delivery/verify_shift.gd headless
    case_run save_resume ../indoor_delivery/resume.gd headless "--checkpoints=$run/teaching"
    case_run counter ../vertical_run/reopen.gd headless "--from=$run/teaching/completed.cfg" --counter
    case_run single ../indoor_delivery/free_order.gd headless "--checkpoints=$run/teaching"
    case_run lunch ../lunch_run/verify.gd headless --practice-lunch
    case_run market ../outer_neighborhood/market_entry.gd headless --explore-500 --outer-market
    case_run repair ../repair_court/walk.gd headless --explore-500 --repair-court
}

roads() {
    case_run ground ../district_age/audit.gd headless
    local direction batch
    for direction in out back; do
        local -a options=()
        if [[ "$direction" == back ]]; then options+=(--reverse); fi
        for batch in 0 1 2; do
            case_run "player_${direction}_$batch" ../district_age/drive_matrix.gd headless "--batch=$batch" "${options[@]}"
        done
    done
}

visual() {
    case_run north entry_corner/north.gd native
    case_run ride patrol.gd native
    case_run turns junctions.gd native
    case_run older_crossings legacy_views.gd native --practice-passage
    case_run junction_profiles entry_corner/verify.gd native --practice-passage
    case_run sites sites.gd native --practice-passage
    case_run home local_route.gd native --practice-passage
    case_run bridge ../vertical_run/verify.gd native --practice-passage
    case_run restore ../vertical_run/reopen.gd headless "--from=$run/bridge/bridge.cfg"
}

initialize() {
    git rev-parse HEAD > "$run/starting-checkout.txt"
    "$godot" --version > "$run/godot-version.txt"
    "$blender" --version > "$run/blender-version.txt"
    date -Is > "$run/start.txt"
    sha256sum work/project/chongqing_godot_v05/scripts/district_500.gd \
        work/project/chongqing_godot_v05/assets/district_500/acceptance-*.{glb,json} \
        work/project/chongqing_godot_v05/assets/district_500/acceptance_textures/*.jpg > "$run/runtime.sha256"
    df -h /workspace /dev/shm > "$run/start-storage.txt"
}

case "$phase" in
    initialize) initialize;;
    state) state;;
    roads) roads;;
    visual) visual;;
    timing) case_run timing ../vertical_run/timing.gd timing --practice-passage;;
    software-timing) case_run software-frame-intervals ../district_refresh/acceptance/combined/software-frame-intervals.gd software-timing --practice-passage;;
    report)
        python3 "$scene/entry_corner/report.py" "$run" > "$run/official-report.log" 2>&1 || {
            code=$?
            printf '%s\n' "$code" > "$run/official-report-exit.txt"
            exit "$code"
        }
        printf '0\n' > "$run/official-report-exit.txt"
        ;;
    all)
        initialize
        if [[ "$concurrency" = 2 ]]; then
            state & state_pid=$!
            roads & roads_pid=$!
            wait "$state_pid"
            wait "$roads_pid"
        else
            state
            roads
        fi
        visual
        case_run timing ../vertical_run/timing.gd timing --practice-passage
        bash "$0" "$run" report
        ;;
    *) printf 'Unknown phase %s\n' "$phase" >&2; exit 2;;
esac
