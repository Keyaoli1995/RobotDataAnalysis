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

