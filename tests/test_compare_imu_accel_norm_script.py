import json
from pathlib import Path

from scripts.compare_imu_accel_norm import (
    DEFAULT_RAWIMUSX_CSV,
    DEFAULT_TCP_RAW_IMU_CSV,
    build_output_summary,
    build_parser,
    resolve_run_paths,
)


def test_resolve_run_paths_uses_local_config_output_dir_for_ide_run(tmp_path):
    output_dir = tmp_path / "csv_output"
    config_path = tmp_path / "local_run.json"
    config_path.write_text(json.dumps({"output_dir": str(output_dir)}), encoding="utf-8")
    args = build_parser().parse_args(["--config", str(config_path)])

    run_paths = resolve_run_paths(args)

    assert run_paths.rawimusx_csv == output_dir / DEFAULT_RAWIMUSX_CSV
    assert run_paths.tcp_raw_imu_csv == output_dir / DEFAULT_TCP_RAW_IMU_CSV
    assert run_paths.output == output_dir / "imu_accel_norm_comparison.png"
    assert run_paths.html_output == output_dir / "imu_accel_norm_comparison.html"
    assert run_paths.rawimusx_axes_output == output_dir / "rawimusx_imu_axes.html"
    assert run_paths.tcp_raw_imu_axes_output == output_dir / "tcp_raw_imu_imu_axes.html"
    assert run_paths.time_intervals_output == output_dir / "imu_time_intervals.html"


def test_resolve_run_paths_keeps_explicit_cli_paths(tmp_path):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(json.dumps({"output_dir": str(tmp_path / "csv_output")}), encoding="utf-8")
    rawimusx_csv = tmp_path / "rawimusx.csv"
    tcp_raw_imu_csv = tmp_path / "tcp.csv"
    output = tmp_path / "plot.png"
    html_output = tmp_path / "plot.html"
    rawimusx_axes_output = tmp_path / "rawimusx_axes.html"
    tcp_raw_imu_axes_output = tmp_path / "tcp_axes.html"
    time_intervals_output = tmp_path / "intervals.html"
    args = build_parser().parse_args(
        [
            str(rawimusx_csv),
            str(tcp_raw_imu_csv),
            "--config",
            str(config_path),
            "--output",
            str(output),
            "--html-output",
            str(html_output),
            "--rawimusx-axes-output",
            str(rawimusx_axes_output),
            "--tcp-raw-imu-axes-output",
            str(tcp_raw_imu_axes_output),
            "--time-intervals-output",
            str(time_intervals_output),
        ]
    )

    run_paths = resolve_run_paths(args)

    assert run_paths.rawimusx_csv == rawimusx_csv
    assert run_paths.tcp_raw_imu_csv == tcp_raw_imu_csv
    assert run_paths.output == output
    assert run_paths.html_output == html_output
    assert run_paths.rawimusx_axes_output == rawimusx_axes_output
    assert run_paths.tcp_raw_imu_axes_output == tcp_raw_imu_axes_output
    assert run_paths.time_intervals_output == time_intervals_output


def test_build_output_summary_includes_source_axis_means():
    comparison_summary = {"aligned_rows": 2}
    left_summary = {
        "accel_mean": {"x": 1.0, "y": 2.0, "z": 3.0},
        "gyro_mean": {"x": 0.1, "y": 0.2, "z": 0.3},
    }
    right_summary = {
        "accel_mean": {"x": 4.0, "y": 5.0, "z": 6.0},
        "gyro_mean": {"x": 0.4, "y": 0.5, "z": 0.6},
    }
    left_timing = {"mean_interval_seconds": 0.01}
    right_timing = {"mean_interval_seconds": 0.02}

    output = build_output_summary(comparison_summary, left_summary, right_summary, left_timing, right_timing)

    assert output == {
        "comparison": {"aligned_rows": 2},
        "sources": {
            "rawimusx": {
                "axes": left_summary,
                "time_intervals": left_timing,
            },
            "tcp_raw_imu": {
                "axes": right_summary,
                "time_intervals": right_timing,
            },
        },
    }
