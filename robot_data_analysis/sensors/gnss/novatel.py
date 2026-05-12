"""NovAtel GNSS CSV parsers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from robot_data_analysis.core.errors import MissingColumnsError
from robot_data_analysis.core.schema import GNSS_COLUMNS
from robot_data_analysis.core.time import add_readable_time
from robot_data_analysis.io.csv import read_csv

POSITION_TYPE_MAPPING = {
    0: "NONE",
    16: "SINGLE",
    17: "PSRDIFF",
    18: "WAAS",
    34: "L1_FLOAT",
    48: "L1_INT",
    50: "NARROW_FLOAT",
    51: "NARROW_INT",
}

BESTGNSSPOS_COLUMN_MAP = {
    "hgt": "height",
    "lat_stdev": "lat_std",
    "lon_stdev": "lon_std",
    "hgt_stdev": "height_std",
    "pos_type.type": "position_type",
    "sol_status.status": "solution_status",
    "num_svs": "num_sats",
    "num_sol_svs": "num_solution_sats",
}

REQUIRED_BESTGNSSPOS_COLUMNS = [
    "timestamp",
    "lat",
    "lon",
    "hgt",
    "lat_stdev",
    "lon_stdev",
    "hgt_stdev",
    "pos_type.type",
    "sol_status.status",
    "num_svs",
    "num_sol_svs",
]


def parse_bestgnsspos_csv(path: str | Path) -> pd.DataFrame:
    """Parse a NovAtel BESTGNSSPOS CSV into the standard GNSS schema."""

    df = read_csv(path)
    missing_columns = [column for column in REQUIRED_BESTGNSSPOS_COLUMNS if column not in df.columns]
    if missing_columns:
        raise MissingColumnsError(missing_columns)

    normalized = df[REQUIRED_BESTGNSSPOS_COLUMNS].rename(columns=BESTGNSSPOS_COLUMN_MAP)
    normalized = add_readable_time(normalized)
    normalized["position_type_desc"] = normalized["position_type"].map(POSITION_TYPE_MAPPING)

    return normalized[GNSS_COLUMNS].copy()

