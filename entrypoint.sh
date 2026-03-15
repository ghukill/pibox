#!/usr/bin/env bash
set -euo pipefail

PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
PI_SKILLS_DIR="$PI_AGENT_DIR/skills"

mkdir -p "$PI_SKILLS_DIR"

# Bootstrap baked-in global defaults into persisted ~/.pi only when missing.
if [ -d "${PIBOX_DEFAULTS_DIR:-}" ]; then
  # Copy default top-level files like AGENTS.md, APPEND_SYSTEM.md
  for default_file in "${PIBOX_DEFAULTS_DIR}"/*; do
    [ -f "$default_file" ] || continue
    target_file="$PI_AGENT_DIR/$(basename "$default_file")"
    if [ ! -e "$target_file" ]; then
      cp "$default_file" "$target_file"
    fi
  done
fi

# Bootstrap baked-in skills into persisted ~/.pi only when missing.
# This keeps image-provided defaults while preserving user modifications.
if [ -d "${PIBOX_SKILLS_DIR:-}" ]; then
  for skill_path in "${PIBOX_SKILLS_DIR}"/*; do
    [ -d "$skill_path" ] || continue
    skill_name="$(basename "$skill_path")"
    target_path="$PI_SKILLS_DIR/$skill_name"

    if [ ! -e "$target_path" ]; then
      cp -R "$skill_path" "$target_path"
    fi
  done
fi

# If no args, run pi. If args begin with '-', treat them as pi flags.
if [ "$#" -eq 0 ]; then
  set -- pi
elif [[ "$1" == -* ]]; then
  set -- pi "$@"
fi

if [ "$1" = "pi" ]; then
  echo "Welcome to pibox! Ready to help you work on this project."
fi

exec "$@"
