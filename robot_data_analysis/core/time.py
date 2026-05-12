"""Time conversion and sampling helpers."""

from __future__ import annotations

import pandas as pd

from robot_data_analysis.core.schema import READABLE_TIME_COLUMN, TIMESTAMP_COLUMN


def add_readable_time(
    df: pd.DataFrame,
    timestamp_col: str = TIMESTAMP_COLUMN,
    output_col: str = READABLE_TIME_COLUMN,
    unit: str = "ns",
) -> pd.DataFrame:
    """Return a copy of *df* with a datetime column derived from timestamps."""

    result = df.copy()
    result[output_col] = pd.to_datetime(result[timestamp_col], unit=unit)
    return result


def duration_seconds(df: pd.DataFrame, timestamp_col: str = TIMESTAMP_COLUMN) -> float:
    """Return timestamp range duration in seconds for nanosecond timestamps."""

    if df.empty or timestamp_col not in df.columns:
        return 0.0
    timestamps = pd.to_numeric(df[timestamp_col], errors="coerce").dropna()
    if timestamps.empty:
        return 0.0
    return float((timestamps.max() - timestamps.min()) / 1_000_000_000)


def estimated_frequency_hz(
    df: pd.DataFrame,
    timestamp_col: str = TIMESTAMP_COLUMN,
) -> float | None:
    """Estimate sample frequency from row count and timestamp duration."""

    seconds = duration_seconds(df, timestamp_col)
    if seconds <= 0 or len(df) < 2:
        return None
    return round((len(df) - 1) / seconds, 6)

