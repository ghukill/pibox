#!/usr/bin/env bash
# Build and launch pi in a Docker container with mounts to CWD and ~/.pi

set -euo pipefail

IMAGE_NAME="${PIBOX_IMAGE:-pibox}"

# Forward common API key env vars if set (optional alongside /login auth)
ENV_ARGS=()
for var in \
  ANTHROPIC_API_KEY \
  OPENAI_API_KEY \
  GEMINI_API_KEY \
  AZURE_OPENAI_API_KEY \
  MISTRAL_API_KEY \
  GROQ_API_KEY \
  XAI_API_KEY \
  OPENROUTER_API_KEY
 do
  if [ -n "${!var:-}" ]; then
    ENV_ARGS+=(--env "${var}=${!var}")
  fi
done

# Build image
docker build --tag "$IMAGE_NAME" .

# Run pi from any repository with persisted auth/session state in ~/.pi
exec docker run --rm -it \
  --workdir /workdir \
  --volume "$PWD:/workdir" \
  --volume "$HOME/.pi:/home/pi/.pi" \
  "${ENV_ARGS[@]}" \
  "$IMAGE_NAME" "$@"
