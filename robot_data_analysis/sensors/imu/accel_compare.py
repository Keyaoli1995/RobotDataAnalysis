"""Acceleration norm comparison helpers for IMU CSV exports."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from robot_data_analysis.core.errors import MissingColumnsError
from robot_data_analysis.core.schema import READABLE_TIME_COLUMN, TIMESTAMP_COLUMN
from robot_data_analysis.sensors.imu.standardize import parse_imu_csv

ACCEL_NORM_COLUMN = "accel_norm"
TIME_NS_COLUMN = "time_ns"
TIME_SECONDS_COLUMN = "time_seconds"
DEFAULT_IMU_AXES = ("accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z")


def prepare_accel_norm_series(
    df: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    """Build an acceleration norm time series from a standard IMU DataFrame."""

    _require_standard_imu_columns(df)
    accel_values = df.loc[:, ["accel_x", "accel_y", "accel_z"]].apply(pd.to_numeric, errors="coerce")
    time_values = pd.to_numeric(df[TIMESTAMP_COLUMN], errors="coerce")

    result = pd.DataFrame(
        {
            TIME_NS_COLUMN: time_values,
            f"{label}_{ACCEL_NORM_COLUMN}": np.sqrt((accel_values**2).sum(axis=1, skipna=False)),
        }
    ).dropna()
    result = result.sort_values(TIME_NS_COLUMN).reset_index(drop=True)
    if result.empty:
        result[TIME_SECONDS_COLUMN] = []
        return result[[TIME_NS_COLUMN, TIME_SECONDS_COLUMN, f"{label}_{ACCEL_NORM_COLUMN}"]]

    result[TIME_SECONDS_COLUMN] = (result[TIME_NS_COLUMN] - result[TIME_NS_COLUMN].iloc[0]) / 1_000_000_000
    result[READABLE_TIME_COLUMN] = pd.to_datetime(result[TIME_NS_COLUMN], unit="ns")
    return result[[TIME_NS_COLUMN, TIME_SECONDS_COLUMN, f"{label}_{ACCEL_NORM_COLUMN}"]]


def compare_accel_norms(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
    tolerance_ns: int | None = None,
) -> pd.DataFrame:
    """Align two standard IMU DataFrames by nearest timestamp and compare norms."""

    left = prepare_accel_norm_series(left_df, left_label)
    right = prepare_accel_norm_series(right_df, right_label).drop(columns=[TIME_SECONDS_COLUMN])
    left_norm_col = f"{left_label}_{ACCEL_NORM_COLUMN}"
    right_norm_col = f"{right_label}_{ACCEL_NORM_COLUMN}"

    aligned = pd.merge_asof(
        left,
        right,
        on=TIME_NS_COLUMN,
        direction="nearest",
        tolerance=tolerance_ns,
    ).dropna(subset=[right_norm_col])

    aligned[READABLE_TIME_COLUMN] = pd.to_datetime(aligned[TIME_NS_COLUMN], unit="ns")
    aligned["accel_norm_delta"] = aligned[left_norm_col] - aligned[right_norm_col]
    aligned["abs_accel_norm_delta"] = aligned["accel_norm_delta"].abs()
    return aligned[
        [
            TIME_NS_COLUMN,
            TIME_SECONDS_COLUMN,
            READABLE_TIME_COLUMN,
            left_norm_col,
            right_norm_col,
            "accel_norm_delta",
            "abs_accel_norm_delta",
        ]
    ].reset_index(drop=True)


def prepare_imu_axes_series(
    df: pd.DataFrame,
    label: str,
    axes: list[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Build a labeled multi-axis IMU time series from a standard IMU DataFrame."""

    axis_columns = list(axes) if axes else list(DEFAULT_IMU_AXES)
    _require_standard_imu_columns(df, axis_columns)

    time_values = pd.to_numeric(df[TIMESTAMP_COLUMN], errors="coerce")
    axis_values = df.loc[:, axis_columns].apply(pd.to_numeric, errors="coerce")

    result = pd.DataFrame({TIME_NS_COLUMN: time_values})
    for axis_column in axis_columns:
        result[f"{label}_{axis_column}"] = axis_values[axis_column]

    value_columns = [f"{label}_{axis_column}" for axis_column in axis_columns]
    result = result.dropna(subset=[TIME_NS_COLUMN, *value_columns])
    result = result.sort_values(TIME_NS_COLUMN).reset_index(drop=True)
    if result.empty:
        result[TIME_SECONDS_COLUMN] = []
        result[READABLE_TIME_COLUMN] = []
        return result[[TIME_NS_COLUMN, TIME_SECONDS_COLUMN, READABLE_TIME_COLUMN, *value_columns]]

    result[TIME_SECONDS_COLUMN] = (result[TIME_NS_COLUMN] - result[TIME_NS_COLUMN].iloc[0]) / 1_000_000_000
    result[READABLE_TIME_COLUMN] = pd.to_datetime(result[TIME_NS_COLUMN], unit="ns")
    return result[[TIME_NS_COLUMN, TIME_SECONDS_COLUMN, READABLE_TIME_COLUMN, *value_columns]]


def compare_imu_axes(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    axes: list[str] | tuple[str, ...] | None = None,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
    tolerance_ns: int | None = None,
) -> pd.DataFrame:
    """Align two standard IMU DataFrames by nearest timestamp and compare axis outputs."""

    axis_columns = list(axes) if axes else list(DEFAULT_IMU_AXES)
    left = prepare_imu_axes_series(left_df, left_label, axis_columns)
    right = prepare_imu_axes_series(right_df, right_label, axis_columns).drop(
        columns=[TIME_SECONDS_COLUMN, READABLE_TIME_COLUMN]
    )

    right_value_columns = [f"{right_label}_{axis_column}" for axis_column in axis_columns]
    aligned = pd.merge_asof(
        left,
        right,
        on=TIME_NS_COLUMN,
        direction="nearest",
        tolerance=tolerance_ns,
    ).dropna(subset=right_value_columns)

    output_columns = [TIME_NS_COLUMN, TIME_SECONDS_COLUMN, READABLE_TIME_COLUMN]
    for axis_column in axis_columns:
        left_col = f"{left_label}_{axis_column}"
        right_col = f"{right_label}_{axis_column}"
        delta_col = f"{axis_column}_delta"
        aligned[delta_col] = aligned[left_col] - aligned[right_col]
        output_columns.extend([left_col, right_col, delta_col])

    return aligned[output_columns].reset_index(drop=True)


def compare_accel_norm_csvs(
    left_csv: str | Path,
    right_csv: str | Path,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
    tolerance_ns: int | None = None,
) -> pd.DataFrame:
    """Read two IMU CSVs, align their acceleration norms, and return comparison rows."""

    return compare_accel_norms(
        parse_imu_csv(left_csv),
        parse_imu_csv(right_csv),
        left_label=left_label,
        right_label=right_label,
        tolerance_ns=tolerance_ns,
    )


def summarize_accel_norm_comparison(comparison: pd.DataFrame) -> dict[str, float | int | None]:
    """Return a compact JSON-friendly summary for an acceleration norm comparison."""

    if comparison.empty:
        return {
            "aligned_rows": 0,
            "mean_abs_delta": None,
            "max_abs_delta": None,
            "rms_delta": None,
        }

    delta = comparison["accel_norm_delta"]
    abs_delta = comparison["abs_accel_norm_delta"]
    return {
        "aligned_rows": int(len(comparison)),
        "mean_abs_delta": float(abs_delta.mean()),
        "max_abs_delta": float(abs_delta.max()),
        "rms_delta": float(np.sqrt((delta**2).mean())),
    }


def _require_standard_imu_columns(df: pd.DataFrame, axes: list[str] | tuple[str, ...] | None = None) -> None:
    required_columns = [TIMESTAMP_COLUMN, *(axes or ("accel_x", "accel_y", "accel_z"))]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise MissingColumnsError(missing_columns)
