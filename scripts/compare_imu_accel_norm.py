#!/usr/bin/env python3
"""Compare acceleration norm between NovAtel RAWIMUSX and TCP raw IMU CSVs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from robot_data_analysis.sensors.imu.accel_compare import (  # noqa: E402
    compare_accel_norm_csvs,
    summarize_accel_norm_comparison,
)
from robot_data_analysis.visualization.imu import plot_accel_norm_comparison  # noqa: E402

DEFAULT_RAWIMUSX_CSV = Path("novatel_oem7_rawimusx.csv")
DEFAULT_TCP_RAW_IMU_CSV = Path("novatel_oem7_tcp_raw_imu.csv")
DEFAULT_OUTPUT = Path("imu_accel_norm_comparison.png")
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "local_run.json"


@dataclass(frozen=True)
class ImuCompareRunPaths:
    """Resolved input and output paths for one IMU comparison run."""

    rawimusx_csv: Path
    tcp_raw_imu_csv: Path
    output: Path
    aligned_output: Path | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare acceleration norms from novatel_oem7_rawimusx.csv and novatel_oem7_tcp_raw_imu.csv"
    )
    parser.add_argument(
        "rawimusx_csv",
        nargs="?",
        default=None,
        help="path to novatel_oem7_rawimusx.csv",
    )
    parser.add_argument(
        "tcp_raw_imu_csv",
        nargs="?",
        default=None,
        help="path to novatel_oem7_tcp_raw_imu.csv",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="local run config JSON used when CSV paths are omitted",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="output plot path",
    )
    parser.add_argument(
        "--aligned-output",
        help="optional CSV path for the aligned comparison table",
    )
    parser.add_argument(
        "--tolerance-ns",
        type=int,
        default=None,
        help="optional nearest-neighbor alignment tolerance in nanoseconds",
    )
    return parser


def resolve_run_paths(args: argparse.Namespace) -> ImuCompareRunPaths:
    """Resolve script paths for CLI usage or IDE one-click usage."""

    config_output_dir = _load_config_output_dir(args.config)
    base_dir = config_output_dir or Path.cwd()

    rawimusx_csv = Path(args.rawimusx_csv) if args.rawimusx_csv else base_dir / DEFAULT_RAWIMUSX_CSV
    tcp_raw_imu_csv = Path(args.tcp_raw_imu_csv) if args.tcp_raw_imu_csv else base_dir / DEFAULT_TCP_RAW_IMU_CSV
    output = Path(args.output) if args.output else base_dir / DEFAULT_OUTPUT
    aligned_output = Path(args.aligned_output) if args.aligned_output else None

    return ImuCompareRunPaths(
        rawimusx_csv=rawimusx_csv,
        tcp_raw_imu_csv=tcp_raw_imu_csv,
        output=output,
        aligned_output=aligned_output,
    )


def _load_config_output_dir(config_path: str | Path) -> Path | None:
    path = Path(config_path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)

    output_dir = raw_config.get("output_dir")
    if not output_dir:
        return None
    return Path(output_dir).expanduser()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_paths = resolve_run_paths(args)

    comparison = compare_accel_norm_csvs(
        run_paths.rawimusx_csv,
        run_paths.tcp_raw_imu_csv,
        left_label="rawimusx",
        right_label="tcp_raw_imu",
        tolerance_ns=args.tolerance_ns,
    )
    plot_path = plot_accel_norm_comparison(
        comparison,
        run_paths.output,
        left_label="rawimusx",
        right_label="tcp_raw_imu",
    )

    if run_paths.aligned_output:
        run_paths.aligned_output.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(run_paths.aligned_output, index=False)
        print(f"wrote aligned comparison CSV: {run_paths.aligned_output}")

    print(f"wrote plot: {plot_path}")
    print(json.dumps(summarize_accel_norm_comparison(comparison), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
