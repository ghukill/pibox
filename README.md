# pibox

A Dockerized `pi` environment that can be launched from any repository, with persistent auth/session data via host `~/.pi`.

## What this image provides

- `pi` installed globally
- Non-root runtime user (`pi`)
- Baked-in default skills stored in image at `/opt/pibox/skills`
- Baked-in defaults (prompt + settings) stored in image at `/opt/pibox/defaults/`
- Startup bootstrap that copies baked-in defaults into `~/.pi/agent/` if missing

This avoids the common mount issue where `-v ~/.pi:...` hides anything baked into `~/.pi` in the image.

## Included baked-in skill

- `hello-world` (`skills/hello-world/SKILL.md`)
  - When invoked, it should respond with exactly: `🌍`

## Recommended workflow (uv + pibox-cli)

From this repo:

```bash
uv run pibox-cli install
```

This will:

1. Build the Docker image (`pibox` by default)
2. Install a launcher script at `~/.local/bin/pibox`

Then from any repo:

```bash
pibox
```

Or pass normal `pi` args through:

```bash
pibox -p "summarize this repo"
```

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

So coworkers can customize their local files without them being overwritten every run.
