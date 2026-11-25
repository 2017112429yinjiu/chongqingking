#!/usr/bin/env bash
# Install user-owned, pinned tools for this checkout. Ubuntu x86-64.
set -euo pipefail
if [[ "$(uname -sm)" != "Linux x86_64" ]]; then
    echo "Expected Linux x86_64" >&2
    exit 1
fi
root="${CQ_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
tools="$root/.cloud-dev/tools"
mkdir -p "$tools/bin"
scratch=$(mktemp -d "$tools/install.XXXXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
fetch() {
    curl --fail --location --silent --show-error --retry 4 "$1" -o "$scratch/$2"
    (cd "$scratch" && echo "$3  $2" | sha256sum --check -)
}

if [[ ! -x "$tools/bin/git-lfs" ]]; then
    file=git-lfs-linux-amd64-v3.8.1.tar.gz
    fetch "https://github.com/git-lfs/git-lfs/releases/download/v3.8.1/$file" "$file" \
        e72cf723a4a660438862282e8aecf3885fc8123e88bfcad534cf6b941a354b75
    tar -xzf "$scratch/$file" -C "$scratch"
    install -m 0755 "$scratch/git-lfs-3.8.1/git-lfs" "$tools/bin/git-lfs"
fi
export PATH="$tools/bin:$PATH"
if [[ ! -x "$tools/bin/godot" ]]; then
    file=Godot_v4.6.3-stable_linux.x86_64.zip
    fetch "https://github.com/godotengine/godot-builds/releases/download/4.6.3-stable/$file" "$file" \
        d0bc2113065e481c9c2c2b2c37daa4e8be3fe9e27f0ab9ab0b6096e9a37907f3
    unzip -q "$scratch/$file" -d "$scratch"
    install -m 0755 "$scratch/${file%.zip}" "$tools/bin/godot"
fi
if [[ ! -x "$tools/blender-4.3.2-linux-x64/blender" ]]; then
    file=blender-4.3.2-linux-x64.tar.xz
    fetch "https://download.blender.org/release/Blender4.3/$file" "$file" \
        4da1c956673c0485e63054e563ee69198cc8f80d8157dd7592dffc8a6a5592e6
    tar -xJf "$scratch/$file" -C "$scratch"
    mv "$scratch/blender-4.3.2-linux-x64" "$tools/"
fi
ln -sfn ../blender-4.3.2-linux-x64/blender "$tools/bin/blender"
"$tools/bin/godot" --version
"$tools/bin/blender" --version
git lfs install --local
