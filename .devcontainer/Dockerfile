FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl fonts-noto-cjk git-lfs libasound2t64 libegl1 libfontconfig1 libgl1 \
    libsm6 libx11-6 libxcursor1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 \
    libxrandr2 libxrender1 libxxf86vm1 python3 unzip xz-utils \
    && rm -rf /var/lib/apt/lists/*
