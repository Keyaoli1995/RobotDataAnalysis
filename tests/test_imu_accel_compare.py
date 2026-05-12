import numpy as np
import pandas as pd

from robot_data_analysis.sensors.imu.accel_compare import (
    compare_accel_norm_csvs,
    compare_accel_norms,
    prepare_accel_norm_series,
)


def test_prepare_accel_norm_series_uses_standard_imu_columns():
    df = pd.DataFrame(
        {
            "timestamp": [100, 200],
            "accel_x": [3.0, 0.0],
            "accel_y": [4.0, 5.0],
            "accel_z": [12.0, 12.0],
        }
    )

    series = prepare_accel_norm_series(df, "rawimusx")

    assert list(series.columns) == ["time_ns", "time_seconds", "rawimusx_accel_norm"]
    np.testing.assert_allclose(series["rawimusx_accel_norm"], [13.0, 13.0])
    np.testing.assert_allclose(series["time_seconds"], [0.0, 0.0000001])


def test_compare_accel_norms_aligns_by_header_timestamp():
    rawimusx = pd.DataFrame(
        {
            "timestamp": [10_000_000_000, 10_000_000_100],
            "accel_x": [3.0, 0.0],
            "accel_y": [4.0, 5.0],
            "accel_z": [12.0, 12.0],
        }
    )
    tcp_raw_imu = pd.DataFrame(
        {
            "timestamp": [10_000_000_005, 10_000_000_105],
            "accel_x": [0.0, 8.0],
            "accel_y": [0.0, 6.0],
            "accel_z": [12.0, 0.0],
        }
    )

    comparison = compare_accel_norms(
        rawimusx,
        tcp_raw_imu,
        left_label="rawimusx",
        right_label="tcp_raw_imu",
    )

    assert list(comparison.columns) == [
        "time_ns",
        "time_seconds",
        "rawimusx_accel_norm",
        "tcp_raw_imu_accel_norm",
        "accel_norm_delta",
        "abs_accel_norm_delta",
    ]
    np.testing.assert_allclose(comparison["rawimusx_accel_norm"], [13.0, 13.0])
    np.testing.assert_allclose(comparison["tcp_raw_imu_accel_norm"], [12.0, 10.0])
    np.testing.assert_allclose(comparison["accel_norm_delta"], [1.0, 3.0])


def test_compare_accel_norm_csvs_normalizes_exported_novatel_column_names(tmp_path):
    rawimusx_csv = tmp_path / "novatel_oem7_rawimusx.csv"
    tcp_raw_imu_csv = tmp_path / "novatel_oem7_tcp_raw_imu.csv"
    pd.DataFrame(
        {
            "header._stamp._sec": [10],
            "header._stamp._nanosec": [0],
            "x_acc": [3.0],
            "y_acc": [4.0],
            "z_acc": [12.0],
            "x_gyro": [0.1],
            "y_gyro": [0.2],
            "z_gyro": [0.3],
        }
    ).to_csv(rawimusx_csv, index=False)
    pd.DataFrame(
        {
            "header._stamp._sec": [10],
            "header._stamp._nanosec": [0],
            "accel[0]": [0.0],
            "accel[1]": [0.0],
            "accel[2]": [12.0],
            "gyro[0]": [0.1],
            "gyro[1]": [0.2],
            "gyro[2]": [0.3],
        }
    ).to_csv(tcp_raw_imu_csv, index=False)

    comparison = compare_accel_norm_csvs(rawimusx_csv, tcp_raw_imu_csv)

    np.testing.assert_allclose(comparison["rawimusx_accel_norm"], [13.0])
    np.testing.assert_allclose(comparison["tcp_raw_imu_accel_norm"], [12.0])
