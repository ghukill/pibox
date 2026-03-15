#!/usr/bin/env bash
# Build and launch pi in a Docker container with mounts to CWD and ~/.pi

set -euo pipefail

IMAGE_NAME="${PIBOX_IMAGE:-pibox}"

# Build image
docker build --tag "$IMAGE_NAME" .

# Run pi from any repository with persisted auth/session state in ~/.pi
exec docker run --rm -it \
  --workdir /workdir \
  --volume "$PWD:/workdir" \
  --volume "$HOME/.pi:/home/pi/.pi" \
  "$IMAGE_NAME" "$@"
