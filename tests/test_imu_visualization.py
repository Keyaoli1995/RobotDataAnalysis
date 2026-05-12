import pandas as pd

from robot_data_analysis.visualization.imu import (
    DEFAULT_IMU_AXES,
    build_time_interval_series,
    build_time_tick_labels,
    resolve_imu_axes,
)


def test_build_time_tick_labels_shows_elapsed_seconds_and_readable_time():
    comparison = pd.DataFrame(
        {
            "time_seconds": [0.0, 1.5],
            "readable_time": pd.to_datetime(
                [
                    "2026-05-12 11:33:36.000000000",
                    "2026-05-12 11:33:37.500000000",
                ]
            ),
        }
    )

    tick_values, tick_labels = build_time_tick_labels(comparison, max_ticks=2, line_break="\n")

    assert tick_values == [0.0, 1.5]
    assert tick_labels == [
        "0.000 s\n2026-05-12 11:33:36.000",
        "1.500 s\n2026-05-12 11:33:37.500",
    ]


def test_resolve_imu_axes_defaults_to_six_standard_axes():
    assert resolve_imu_axes(None) == DEFAULT_IMU_AXES


def test_resolve_imu_axes_accepts_configured_axis_subset():
    assert resolve_imu_axes(["accel_x", "gyro_z"]) == ["accel_x", "gyro_z"]


def test_build_time_interval_series_uses_consecutive_timestamp_deltas():
    imu_data = pd.DataFrame(
        {
            "timestamp": [100, 200, 450],
            "readable_time": pd.to_datetime(
                [
                    "2026-05-12 11:33:36.000000100",
                    "2026-05-12 11:33:36.000000200",
                    "2026-05-12 11:33:36.000000450",
                ]
            ),
        }
    )

    intervals = build_time_interval_series(imu_data, "rawimusx")

    assert list(intervals.columns) == ["time_seconds", "readable_time", "interval_seconds", "source"]
    assert intervals["time_seconds"].tolist() == [0.0000001, 0.00000035]
    assert intervals["interval_seconds"].tolist() == [0.0000001, 0.00000025]
    assert intervals["source"].tolist() == ["rawimusx", "rawimusx"]
