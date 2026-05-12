"""CSV read/write helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv(path: str | Path, strip_leading_underscores: bool = True) -> pd.DataFrame:
    """Read a CSV file and optionally normalize leading underscore column names."""

    df = pd.read_csv(path)
    if strip_leading_underscores:
        df.columns = [column.lstrip("_") for column in df.columns]
    return df


def write_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    """Write a DataFrame to CSV and return the destination path."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=index)
    return destination

