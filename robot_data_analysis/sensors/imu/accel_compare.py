"""Acceleration norm comparison helpers for IMU CSV exports."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from robot_data_analysis.core.errors import MissingColumnsError
from robot_data_analysis.core.schema import TIMESTAMP_COLUMN
from robot_data_analysis.sensors.imu.standardize import parse_imu_csv

ACCEL_NORM_COLUMN = "accel_norm"
TIME_NS_COLUMN = "time_ns"
TIME_SECONDS_COLUMN = "time_seconds"


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

    aligned["accel_norm_delta"] = aligned[left_norm_col] - aligned[right_norm_col]
    aligned["abs_accel_norm_delta"] = aligned["accel_norm_delta"].abs()
    return aligned.reset_index(drop=True)


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


def _require_standard_imu_columns(df: pd.DataFrame) -> None:
    required_columns = [TIMESTAMP_COLUMN, "accel_x", "accel_y", "accel_z"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise MissingColumnsError(missing_columns)
