#!/usr/bin/env python3
"""Management CLI for pibox.

Usage examples:
  uv run pibox-cli install
  uv run pibox-cli update
  uv run pibox-cli uninstall
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import click


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE = "pibox"
DEFAULT_BIN_DIR = Path.home() / ".local" / "bin"
LAUNCHER_NAME = "pibox"

API_ENV_VARS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "XAI_API_KEY",
    "OPENROUTER_API_KEY",
]


def run_cmd(cmd: list[str], *, cwd: Path | None = None) -> None:
    pretty = " ".join(cmd)
    click.echo(f"$ {pretty}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def ensure_docker() -> None:
    if shutil.which("docker") is None:
        raise click.ClickException("docker is not installed or not in PATH")


def build_image(image: str) -> None:
    ensure_docker()
    run_cmd(["docker", "build", "--tag", image, str(REPO_ROOT)])


def launcher_script(image: str) -> str:
    env_lines = "\n".join(
        [
            f'  [ -n "${{{var}:-}}" ] && ENV_ARGS+=(--env "{var}=${{{var}}}")'
            for var in API_ENV_VARS
        ]
    )
    return f"""#!/usr/bin/env bash
set -euo pipefail

IMAGE=\"${{PIBOX_IMAGE:-{image}}}\"
mkdir -p \"$HOME/.pi\"

ENV_ARGS=()
{env_lines}

exec docker run --rm -it \\
  --workdir /workdir \\
  --volume \"$PWD:/workdir\" \\
  --volume \"$HOME/.pi:/home/pi/.pi\" \\
  "${{ENV_ARGS[@]}}" \\
  "$IMAGE" "$@"
"""


def install_launcher(bin_dir: Path, image: str) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher_path = bin_dir / LAUNCHER_NAME
    launcher_path.write_text(launcher_script(image), encoding="utf-8")
    launcher_path.chmod(launcher_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return launcher_path


def path_contains(directory: Path) -> bool:
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    return str(directory) in path_entries


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Manage local pibox image and launcher."""


@main.command()
@click.option("--image", default=DEFAULT_IMAGE, show_default=True, help="Docker image tag")
@click.option(
    "--bin-dir",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=DEFAULT_BIN_DIR,
    show_default=True,
    help="Directory for installed launcher",
)
def install(image: str, bin_dir: Path) -> None:
    """Build image and install pibox launcher."""
    build_image(image)
    launcher = install_launcher(bin_dir, image)
    click.echo(f"Installed launcher: {launcher}")
    if not path_contains(bin_dir):
        click.echo(f"Note: {bin_dir} is not on PATH.")
        click.echo(f'Add this to your shell config: export PATH="{bin_dir}:$PATH"')


@main.command()
@click.option("--image", default=DEFAULT_IMAGE, show_default=True, help="Docker image tag")
@click.option(
    "--bin-dir",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=DEFAULT_BIN_DIR,
    show_default=True,
    help="Directory for installed launcher",
)
@click.option("--no-pull", is_flag=True, help="Skip git pull")
def update(image: str, bin_dir: Path, no_pull: bool) -> None:
    """Pull latest changes, rebuild image, refresh launcher."""
    if not no_pull:
        run_cmd(["git", "pull"], cwd=REPO_ROOT)
    build_image(image)
    launcher = install_launcher(bin_dir, image)
    click.echo(f"Updated launcher: {launcher}")


@main.command()
@click.option(
    "--bin-dir",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=DEFAULT_BIN_DIR,
    show_default=True,
    help="Directory of launcher",
)
def uninstall(bin_dir: Path) -> None:
    """Remove installed pibox launcher."""
    launcher = bin_dir / LAUNCHER_NAME
    if launcher.exists():
        launcher.unlink()
        click.echo(f"Removed launcher: {launcher}")
    else:
        click.echo(f"Launcher not found: {launcher}")


@main.command()
def doctor() -> None:
    """Check local pibox setup."""
    click.echo(f"Repo root: {REPO_ROOT}")
    click.echo(f"Docker: {shutil.which('docker') or 'not found'}")
    click.echo(f"Default launcher path: {DEFAULT_BIN_DIR / LAUNCHER_NAME}")
    click.echo(f"PATH contains {DEFAULT_BIN_DIR}: {path_contains(DEFAULT_BIN_DIR)}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode)
