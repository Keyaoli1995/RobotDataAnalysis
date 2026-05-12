import pandas as pd

from robot_data_analysis.sensors.imu.standardize import normalize_imu_dataframe


def test_normalize_imu_dataframe_uses_header_time_and_preserves_bag_timestamp():
    df = pd.DataFrame(
        {
            "timestamp": [1_700_000_001_000_000_000],
            "header._stamp._sec": [1_700_000_000],
            "header._stamp._nanosec": [123],
            "x_acc": [1.0],
            "y_acc": [2.0],
            "z_acc": [3.0],
            "x_gyro": [0.1],
            "y_gyro": [0.2],
            "z_gyro": [0.3],
        }
    )

    normalized = normalize_imu_dataframe(df)

    assert list(normalized.columns) == [
        "timestamp",
        "readable_time",
        "bag_timestamp",
        "accel_x",
        "accel_y",
        "accel_z",
        "gyro_x",
        "gyro_y",
        "gyro_z",
    ]
    assert normalized.loc[0, "timestamp"] == 1_700_000_000_000_000_123
    assert normalized.loc[0, "bag_timestamp"] == 1_700_000_001_000_000_000
    assert normalized.loc[0, "accel_x"] == 1.0
    assert normalized.loc[0, "gyro_z"] == 0.3


def test_normalize_imu_dataframe_supports_tcp_raw_imu_array_columns():
    df = pd.DataFrame(
        {
            "timestamp": [1_700_000_001_000_000_000],
            "header._stamp._sec": [1_700_000_000],
            "header._stamp._nanosec": [456],
            "accel[0]": [4.0],
            "accel[1]": [5.0],
            "accel[2]": [6.0],
            "gyro[0]": [0.4],
            "gyro[1]": [0.5],
            "gyro[2]": [0.6],
        }
    )

    normalized = normalize_imu_dataframe(df)

    assert normalized.loc[0, "timestamp"] == 1_700_000_000_000_000_456
    assert normalized.loc[0, "bag_timestamp"] == 1_700_000_001_000_000_000
    assert normalized.loc[0, "accel_y"] == 5.0
    assert normalized.loc[0, "gyro_y"] == 0.5


def test_normalize_imu_dataframe_falls_back_to_bag_timestamp_without_header_time():
    df = pd.DataFrame(
        {
            "timestamp": [100],
            "accel_x": [1.0],
            "accel_y": [2.0],
            "accel_z": [2.0],
            "gyro_x": [0.1],
            "gyro_y": [0.2],
            "gyro_z": [0.3],
        }
    )

    normalized = normalize_imu_dataframe(df)

    assert normalized.loc[0, "timestamp"] == 100
    assert normalized.loc[0, "bag_timestamp"] == 100
