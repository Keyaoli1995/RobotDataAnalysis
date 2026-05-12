"""Basic data quality summaries."""

from __future__ import annotations

import pandas as pd

from robot_data_analysis.core.schema import TIMESTAMP_COLUMN
from robot_data_analysis.core.time import duration_seconds, estimated_frequency_hz


def summarize_dataframe(
    df: pd.DataFrame,
    timestamp_col: str = TIMESTAMP_COLUMN,
) -> dict:
    """Return a JSON-friendly quality summary for a DataFrame."""

    summary = {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "null_counts": {column: int(count) for column, count in df.isna().sum().items()},
    }

    if timestamp_col in df.columns and not df.empty:
        timestamps = pd.to_numeric(df[timestamp_col], errors="coerce").dropna()
        summary.update(
            {
                "start_timestamp": int(timestamps.min()) if not timestamps.empty else None,
                "end_timestamp": int(timestamps.max()) if not timestamps.empty else None,
                "duration_seconds": duration_seconds(df, timestamp_col),
                "estimated_hz": estimated_frequency_hz(df, timestamp_col),
                "duplicate_timestamps": int(df[timestamp_col].duplicated().sum()),
            }
        )
    else:
        summary.update(
            {
                "start_timestamp": None,
                "end_timestamp": None,
                "duration_seconds": 0.0,
                "estimated_hz": None,
                "duplicate_timestamps": 0,
            }
        )

    return summary


def summarize_time_intervals(
    df: pd.DataFrame,
    timestamp_col: str = TIMESTAMP_COLUMN,
) -> dict[str, float | int | None]:
    """Return statistics for consecutive timestamp intervals in seconds."""

    if timestamp_col not in df.columns or df.empty:
        return _empty_interval_summary(0)

    timestamps = pd.to_numeric(df[timestamp_col], errors="coerce").dropna().sort_values()
    sample_count = int(len(timestamps))
    if sample_count < 2:
        return _empty_interval_summary(sample_count)

    intervals_seconds = timestamps.diff().dropna() / 1_000_000_000
    median_interval = float(intervals_seconds.median())
    return {
        "sample_count": sample_count,
        "interval_count": int(len(intervals_seconds)),
        "mean_interval_seconds": float(intervals_seconds.mean()),
        "median_interval_seconds": median_interval,
        "min_interval_seconds": float(intervals_seconds.min()),
        "max_interval_seconds": float(intervals_seconds.max()),
        "std_interval_seconds": float(intervals_seconds.std(ddof=0)),
        "p95_interval_seconds": float(intervals_seconds.quantile(0.95)),
        "estimated_hz_from_median_interval": (float(1.0 / median_interval) if median_interval > 0 else None),
        "non_positive_intervals": int((intervals_seconds <= 0).sum()),
    }


def _empty_interval_summary(sample_count: int) -> dict[str, float | int | None]:
    return {
        "sample_count": sample_count,
        "interval_count": 0,
        "mean_interval_seconds": None,
        "median_interval_seconds": None,
        "min_interval_seconds": None,
        "max_interval_seconds": None,
        "std_interval_seconds": None,
        "p95_interval_seconds": None,
        "estimated_hz_from_median_interval": None,
        "non_positive_intervals": 0,
    }
