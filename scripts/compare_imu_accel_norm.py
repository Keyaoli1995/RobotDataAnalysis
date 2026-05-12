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

from robot_data_analysis.analysis.quality import summarize_time_intervals  # noqa: E402
from robot_data_analysis.sensors.imu.accel_compare import (  # noqa: E402
    compare_accel_norms,
    summarize_accel_norm_comparison,
)
from robot_data_analysis.sensors.imu.standardize import parse_imu_csv, summarize_imu_axes  # noqa: E402
from robot_data_analysis.visualization.imu import (  # noqa: E402
    DEFAULT_IMU_AXES,
    plot_accel_norm_comparison,
    plot_imu_axes_outputs,
    plot_interactive_accel_norm_comparison,
    plot_interactive_time_intervals,
)

DEFAULT_RAWIMUSX_CSV = Path("novatel_oem7_rawimusx.csv")
DEFAULT_TCP_RAW_IMU_CSV = Path("novatel_oem7_tcp_raw_imu.csv")
DEFAULT_OUTPUT = Path("imu_accel_norm_comparison.png")
DEFAULT_HTML_OUTPUT = Path("imu_accel_norm_comparison.html")
DEFAULT_RAWIMUSX_AXES_OUTPUT = Path("rawimusx_imu_axes.html")
DEFAULT_TCP_RAW_IMU_AXES_OUTPUT = Path("tcp_raw_imu_imu_axes.html")
DEFAULT_TIME_INTERVALS_OUTPUT = Path("imu_time_intervals.html")
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "local_run.json"


@dataclass(frozen=True)
class ImuCompareRunPaths:
    """Resolved input and output paths for one IMU comparison run."""

    rawimusx_csv: Path
    tcp_raw_imu_csv: Path
    output: Path
    html_output: Path
    rawimusx_axes_output: Path
    tcp_raw_imu_axes_output: Path
    time_intervals_output: Path
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
        "--html-output",
        default=None,
        help="interactive HTML plot path",
    )
    parser.add_argument(
        "--rawimusx-axes-output",
        default=None,
        help="interactive RAWIMUSX six-axis output plot path",
    )
    parser.add_argument(
        "--tcp-raw-imu-axes-output",
        default=None,
        help="interactive TCP raw IMU six-axis output plot path",
    )
    parser.add_argument(
        "--time-intervals-output",
        default=None,
        help="interactive timestamp interval comparison plot path",
    )
    parser.add_argument(
        "--imu-axes",
        default=",".join(DEFAULT_IMU_AXES),
        help="comma-separated standard IMU axes to plot",
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
    html_output = Path(args.html_output) if args.html_output else base_dir / DEFAULT_HTML_OUTPUT
    rawimusx_axes_output = (
        Path(args.rawimusx_axes_output) if args.rawimusx_axes_output else base_dir / DEFAULT_RAWIMUSX_AXES_OUTPUT
    )
    tcp_raw_imu_axes_output = (
        Path(args.tcp_raw_imu_axes_output)
        if args.tcp_raw_imu_axes_output
        else base_dir / DEFAULT_TCP_RAW_IMU_AXES_OUTPUT
    )
    time_intervals_output = (
        Path(args.time_intervals_output) if args.time_intervals_output else base_dir / DEFAULT_TIME_INTERVALS_OUTPUT
    )
    aligned_output = Path(args.aligned_output) if args.aligned_output else None

    return ImuCompareRunPaths(
        rawimusx_csv=rawimusx_csv,
        tcp_raw_imu_csv=tcp_raw_imu_csv,
        output=output,
        html_output=html_output,
        rawimusx_axes_output=rawimusx_axes_output,
        tcp_raw_imu_axes_output=tcp_raw_imu_axes_output,
        time_intervals_output=time_intervals_output,
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


def build_output_summary(
    comparison_summary: dict,
    left_summary: dict,
    right_summary: dict,
    left_timing_summary: dict,
    right_timing_summary: dict,
) -> dict:
    """Build the terminal JSON payload for one comparison run."""

    return {
        "comparison": comparison_summary,
        "sources": {
            "rawimusx": {
                "axes": left_summary,
                "time_intervals": left_timing_summary,
            },
            "tcp_raw_imu": {
                "axes": right_summary,
                "time_intervals": right_timing_summary,
            },
        },
    }


def parse_imu_axes(value: str) -> list[str]:
    """Parse a comma-separated IMU axis list."""

    axes = [axis.strip() for axis in value.split(",") if axis.strip()]
    return axes or DEFAULT_IMU_AXES.copy()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_paths = resolve_run_paths(args)
    imu_axes = parse_imu_axes(args.imu_axes)

    rawimusx = parse_imu_csv(run_paths.rawimusx_csv)
    tcp_raw_imu = parse_imu_csv(run_paths.tcp_raw_imu_csv)
    comparison = compare_accel_norms(
        rawimusx,
        tcp_raw_imu,
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
    html_plot_path = plot_interactive_accel_norm_comparison(
        comparison,
        run_paths.html_output,
        left_label="rawimusx",
        right_label="tcp_raw_imu",
    )
    rawimusx_axes_plot_path = plot_imu_axes_outputs(
        rawimusx,
        run_paths.rawimusx_axes_output,
        axes=imu_axes,
        title="RAWIMUSX IMU outputs",
    )
    tcp_raw_imu_axes_plot_path = plot_imu_axes_outputs(
        tcp_raw_imu,
        run_paths.tcp_raw_imu_axes_output,
        axes=imu_axes,
        title="TCP raw IMU outputs",
    )
    time_intervals_plot_path = plot_interactive_time_intervals(
        rawimusx,
        tcp_raw_imu,
        run_paths.time_intervals_output,
        left_label="rawimusx",
        right_label="tcp_raw_imu",
    )

    if run_paths.aligned_output:
        run_paths.aligned_output.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(run_paths.aligned_output, index=False)
        print(f"wrote aligned comparison CSV: {run_paths.aligned_output}")

    print(f"wrote plot: {plot_path}")
    print(f"wrote interactive plot: {html_plot_path}")
    print(f"wrote rawimusx IMU axes plot: {rawimusx_axes_plot_path}")
    print(f"wrote tcp_raw_imu IMU axes plot: {tcp_raw_imu_axes_plot_path}")
    print(f"wrote IMU time intervals plot: {time_intervals_plot_path}")
    output_summary = build_output_summary(
        summarize_accel_norm_comparison(comparison),
        summarize_imu_axes(rawimusx),
        summarize_imu_axes(tcp_raw_imu),
        summarize_time_intervals(rawimusx),
        summarize_time_intervals(tcp_raw_imu),
    )
    print(json.dumps(output_summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
