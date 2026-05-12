import pandas as pd

from robot_data_analysis.analysis.quality import summarize_dataframe
from robot_data_analysis.core.time import add_readable_time


def test_add_readable_time_returns_copy_with_datetime_column():
    df = pd.DataFrame({"timestamp": [1_700_000_000_000_000_000]})

    converted = add_readable_time(df)

    assert "readable_time" not in df.columns
    assert str(converted.loc[0, "readable_time"]) == "2023-11-14 22:13:20"


def test_summarize_dataframe_reports_time_range_rate_and_nulls():
    df = pd.DataFrame(
        {
            "timestamp": [0, 1_000_000_000, 2_000_000_000, 2_000_000_000],
            "value": [1.0, None, 3.0, 4.0],
        }
    )

    summary = summarize_dataframe(df)

    assert summary["rows"] == 4
    assert summary["columns"] == ["timestamp", "value"]
    assert summary["duration_seconds"] == 2.0
    assert summary["estimated_hz"] == 1.5
    assert summary["duplicate_timestamps"] == 1
    assert summary["null_counts"] == {"timestamp": 0, "value": 1}

