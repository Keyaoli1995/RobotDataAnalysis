import json
from pathlib import Path

from scripts.compare_imu_accel_norm import (
    DEFAULT_RAWIMUSX_CSV,
    DEFAULT_TCP_RAW_IMU_CSV,
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


def test_resolve_run_paths_keeps_explicit_cli_paths(tmp_path):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(json.dumps({"output_dir": str(tmp_path / "csv_output")}), encoding="utf-8")
    rawimusx_csv = tmp_path / "rawimusx.csv"
    tcp_raw_imu_csv = tmp_path / "tcp.csv"
    output = tmp_path / "plot.png"
    args = build_parser().parse_args(
        [
            str(rawimusx_csv),
            str(tcp_raw_imu_csv),
            "--config",
            str(config_path),
            "--output",
            str(output),
        ]
    )

    run_paths = resolve_run_paths(args)

    assert run_paths.rawimusx_csv == rawimusx_csv
    assert run_paths.tcp_raw_imu_csv == tcp_raw_imu_csv
    assert run_paths.output == output
