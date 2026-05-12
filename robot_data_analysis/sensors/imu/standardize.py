"""Normalize exported IMU CSV data to the shared IMU schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from robot_data_analysis.core.errors import MissingColumnsError
from robot_data_analysis.core.schema import (
    BAG_TIMESTAMP_COLUMN,
    IMU_COLUMNS,
    READABLE_TIME_COLUMN,
    TIMESTAMP_COLUMN,
)
from robot_data_analysis.core.time import add_readable_time
from robot_data_analysis.io.csv import read_csv

HEADER_TIME_COLUMN_GROUPS = (
    ("header_stamp_sec", "header_stamp_nanosec"),
    ("header.stamp.sec", "header.stamp.nanosec"),
    ("header._stamp._sec", "header._stamp._nanosec"),
    ("stamp.sec", "stamp.nanosec"),
    ("stamp_sec", "stamp_nanosec"),
)

ACCEL_COLUMN_GROUPS = (
    ("accel_x", "accel_y", "accel_z"),
    ("accel[0]", "accel[1]", "accel[2]"),
    ("linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"),
    ("x_accel_output", "y_accel_output", "z_accel_output"),
    ("x_accel", "y_accel", "z_accel"),
    ("x_acc", "y_acc", "z_acc"),
)

GYRO_COLUMN_GROUPS = (
    ("gyro_x", "gyro_y", "gyro_z"),
    ("gyro[0]", "gyro[1]", "gyro[2]"),
    ("angular_velocity.x", "angular_velocity.y", "angular_velocity.z"),
    ("x_gyro_output", "y_gyro_output", "z_gyro_output"),
    ("x_gyro", "y_gyro", "z_gyro"),
)


def parse_imu_csv(path: str | Path) -> pd.DataFrame:
    """Read and normalize an exported IMU CSV."""

    return normalize_imu_dataframe(read_csv(path, strip_leading_underscores=True))


def normalize_imu_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a standard IMU DataFrame independent of original CSV headers."""

    normalized = pd.DataFrame()
    normalized[TIMESTAMP_COLUMN] = _preferred_timestamp_ns(df)
    normalized[BAG_TIMESTAMP_COLUMN] = _bag_timestamp_ns(df)

    accel_columns = _find_column_group(df, ACCEL_COLUMN_GROUPS, "acceleration")
    gyro_columns = _find_column_group(df, GYRO_COLUMN_GROUPS, "gyro")

    normalized["accel_x"] = pd.to_numeric(df[accel_columns[0]], errors="coerce")
    normalized["accel_y"] = pd.to_numeric(df[accel_columns[1]], errors="coerce")
    normalized["accel_z"] = pd.to_numeric(df[accel_columns[2]], errors="coerce")
    normalized["gyro_x"] = pd.to_numeric(df[gyro_columns[0]], errors="coerce")
    normalized["gyro_y"] = pd.to_numeric(df[gyro_columns[1]], errors="coerce")
    normalized["gyro_z"] = pd.to_numeric(df[gyro_columns[2]], errors="coerce")

    normalized = normalized.dropna(subset=[TIMESTAMP_COLUMN, "accel_x", "accel_y", "accel_z"])
    normalized[TIMESTAMP_COLUMN] = normalized[TIMESTAMP_COLUMN].astype("int64")
    normalized[BAG_TIMESTAMP_COLUMN] = normalized[BAG_TIMESTAMP_COLUMN].astype("int64")
    normalized = add_readable_time(normalized, TIMESTAMP_COLUMN, READABLE_TIME_COLUMN)

    return normalized[IMU_COLUMNS].sort_values(TIMESTAMP_COLUMN).reset_index(drop=True)


def _preferred_timestamp_ns(df: pd.DataFrame) -> pd.Series:
    for sec_col, nsec_col in HEADER_TIME_COLUMN_GROUPS:
        if sec_col in df.columns and nsec_col in df.columns:
            return _combine_sec_nsec(df[sec_col], df[nsec_col])

    if TIMESTAMP_COLUMN in df.columns:
        return pd.to_numeric(df[TIMESTAMP_COLUMN], errors="coerce")

    raise MissingColumnsError(
        [TIMESTAMP_COLUMN, *[column for group in HEADER_TIME_COLUMN_GROUPS for column in group]]
    )


def _bag_timestamp_ns(df: pd.DataFrame) -> pd.Series:
    if TIMESTAMP_COLUMN in df.columns:
        return pd.to_numeric(df[TIMESTAMP_COLUMN], errors="coerce")
    return _preferred_timestamp_ns(df)


def _combine_sec_nsec(seconds: pd.Series, nanoseconds: pd.Series) -> pd.Series:
    return pd.to_numeric(seconds, errors="coerce") * 1_000_000_000 + pd.to_numeric(
        nanoseconds,
        errors="coerce",
    )


def _find_column_group(
    df: pd.DataFrame,
    column_groups: tuple[tuple[str, str, str], ...],
    group_name: str,
) -> tuple[str, str, str]:
    for columns in column_groups:
        if all(column in df.columns for column in columns):
            return columns
    raise MissingColumnsError([f"{group_name}: {' or '.join(group)}" for group in column_groups])
