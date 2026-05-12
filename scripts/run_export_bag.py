#!/usr/bin/env python3
"""IDE-friendly ROS2 bag export runner.

Copy `configs/local_run.example.json` to `configs/local_run.json`, edit the
paths, then run this file directly from your IDE.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from robot_data_analysis.ros.bag_exporter import bag_to_csv

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "local_run.json"
DEFAULT_ROS_SETUP = Path("/opt/ros/humble/setup.bash")
DEFAULT_PYTHON_EXECUTABLE = Path("/usr/bin/python3")


@dataclass(frozen=True)
class ExportBagConfig:
    """Local configuration for one bag export run."""

    bag_path: Path
    output_dir: Path
    ros_setup: Path | None
    workspace_setup: Path
    python_executable: Path


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> ExportBagConfig:
    """Load bag export configuration from a JSON file."""

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"config file not found: {path}. "
            "Copy configs/local_run.example.json to configs/local_run.json and edit paths."
        )

    with path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)

    missing_keys = [key for key in ("bag_path", "output_dir", "workspace_setup") if not raw_config.get(key)]
    if missing_keys:
        raise ValueError(f"missing required config keys: {', '.join(missing_keys)}")

    return ExportBagConfig(
        bag_path=Path(raw_config["bag_path"]).expanduser(),
        output_dir=Path(raw_config["output_dir"]).expanduser(),
        ros_setup=Path(raw_config.get("ros_setup", DEFAULT_ROS_SETUP)).expanduser(),
        workspace_setup=Path(raw_config["workspace_setup"]).expanduser(),
        python_executable=Path(raw_config.get("python_executable", DEFAULT_PYTHON_EXECUTABLE)).expanduser(),
    )


def build_worker_shell_command(
    config: ExportBagConfig,
    config_path: str | Path,
    script_path: str | Path = Path(__file__).resolve(),
) -> str:
    """Build the shell command that prepares ROS and starts the worker."""

    commands = ["set -e"]
    if config.ros_setup:
        commands.append(f"source {shlex.quote(str(config.ros_setup))}")
    if config.workspace_setup:
        commands.append(f"source {shlex.quote(str(config.workspace_setup))}")
    commands.append(
        "exec "
        f"{shlex.quote(str(config.python_executable))} "
        f"{shlex.quote(str(script_path))} "
        "--worker "
        f"--config {shlex.quote(str(config_path))}"
    )
    return "\n".join(commands)


def run_export(config: ExportBagConfig) -> int:
    """Run the actual bag export in an already prepared ROS environment."""

    print(f"bag_path: {config.bag_path}")
    print(f"output_dir: {config.output_dir}")

    written_files = bag_to_csv(config.bag_path, config.output_dir)
    print(f"exported {len(written_files)} CSV files")
    for path in written_files:
        print(path)
    return 0


def launch_worker(config: ExportBagConfig, config_path: str | Path) -> int:
    """Start a worker process after sourcing ROS setup scripts."""

    command = build_worker_shell_command(config, config_path)
    print("Launching ROS bag export worker with configured ROS environment...", flush=True)
    if config.ros_setup:
        print(f"ros_setup: {config.ros_setup}", flush=True)
    if config.workspace_setup:
        print(f"workspace_setup: {config.workspace_setup}", flush=True)
    print(f"python_executable: {config.python_executable}", flush=True)
    completed = subprocess.run(["bash", "-lc", command], cwd=PROJECT_ROOT, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ROS2 bag export from a local JSON config")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="path to local run config JSON",
    )
    parser.add_argument(
        "--worker",
        action="store_true",
        help="internal mode: run export after the launcher has prepared ROS environment",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.worker:
        return run_export(config)
    return launch_worker(config, args.config)


if __name__ == "__main__":
    raise SystemExit(main())
