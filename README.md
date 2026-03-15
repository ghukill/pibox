# pibox

A Dockerized `pi` environment that can be launched from any repository, with persistent auth/session data via host `~/.pi`.

## Quick start

### Prerequisites

- Docker
- [`uv`](https://docs.astral.sh/uv/)
- Git

### Install launcher

From this repo:

```bash
uv run pibox-cli install
```

This will:

1. Build the Docker image (`pibox` by default)
2. Install a launcher script at `~/.local/bin/pibox`

If needed, add `~/.local/bin` to your `PATH`.

### Run from any repository

```bash
pibox
```

Pass normal `pi` args through:

```bash
pibox -p "summarize this repo"
```

On first use, authenticate in the container if needed:

```text
pi /login
```

### Verify setup

```bash
pibox -p "hello"
```

## What this image provides

- `pi` installed globally
- Non-root runtime user (`pi`)
- Baked-in default skills stored in image at `/opt/pibox/skills`
- Baked-in defaults (prompt + settings) stored in image at `/opt/pibox/defaults/`
- Startup bootstrap that copies baked-in defaults into `~/.pi/agent/` if missing

This avoids the common mount issue where `-v ~/.pi:...` hides anything baked into `~/.pi` in the image.

## How it works

`pibox` runs Docker with these key mounts:

- `"$PWD:/workdir"` → your current repository is available in-container at `/workdir`
- `"$HOME/.pi:/home/pi/.pi"` → your auth/session/config persist across runs

Common API keys are forwarded only if set in your host environment:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `MISTRAL_API_KEY`
- `GROQ_API_KEY`
- `XAI_API_KEY`
- `OPENROUTER_API_KEY`

## Included baked-in skill

- `hello-world` (`skills/hello-world/SKILL.md`)
  - When invoked, it should respond with exactly: `🌍`

## CLI commands

### Update

```bash
uv run pibox-cli update
```

By default this runs `git pull`, rebuilds the image, and refreshes the launcher.

### Uninstall launcher

```bash
uv run pibox-cli uninstall
```

### Diagnostics

```bash
uv run pibox-cli doctor
```

## Development

Run linting, formatting, and type checks:

```bash
ruff check .
ruff format .
ty .
```

## Troubleshooting

- **`pibox` command not found**
  - Ensure `~/.local/bin` is on your `PATH`.
- **Not authenticated in container**
  - Run `pi /login` inside `pibox`.
- **Unexpected file ownership/permissions on mounted files**
  - Check host file ownership and permissions for the mounted repo.

## Legacy workflow

You can still use the direct shell wrapper:

```bash
./run.sh
```

## Bootstrap behavior (defaults + skills)

On container startup, `entrypoint.sh` copies baked-in defaults from:

- `/opt/pibox/defaults/*` (including `settings.json` with `quietStartup: true`)

into:

- `/home/pi/.pi/agent/*`

and copies each baked-in skill from:

- `/opt/pibox/skills/<skill-name>`

into:

- `/home/pi/.pi/agent/skills/<skill-name>`

Both are copied **only if the target does not already exist**.

So users can customize their local files without them being overwritten every run.
