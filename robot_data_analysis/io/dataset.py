"""Experiment directory scanning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from robot_data_analysis.core.schema import SensorType


@dataclass(frozen=True)
class DatasetFile:
    """Metadata for one CSV file in an experiment directory."""

    path: Path
    name: str
    sensor_type: str
    row_count: int
    columns: list[str]


def detect_sensor_type(path: str | Path) -> str:
    """Infer a broad sensor type from a CSV filename."""

    name = Path(path).name.lower()
    if any(token in name for token in ("bestgnsspos", "gnss", "gps", "novatel")):
        return SensorType.GNSS.value
    if "imu" in name:
        return SensorType.IMU.value
    if any(token in name for token in ("ins", "inspva", "odom")):
        return SensorType.INS.value
    return SensorType.UNKNOWN.value


def scan_csv_files(root: str | Path) -> list[DatasetFile]:
    """Scan an experiment directory and return metadata for CSV files."""

    root_path = Path(root)
    files = []
    for csv_path in sorted(root_path.rglob("*.csv"), key=lambda item: item.name):
        df = pd.read_csv(csv_path)
        files.append(
            DatasetFile(
                path=csv_path,
                name=csv_path.name,
                sensor_type=detect_sensor_type(csv_path),
                row_count=int(len(df)),
                columns=list(df.columns),
            )
        )
    return files

