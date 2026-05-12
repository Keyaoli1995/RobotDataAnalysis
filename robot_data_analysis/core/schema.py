"""Shared sensor schema definitions."""

from __future__ import annotations

from enum import StrEnum


class SensorType(StrEnum):
    """Supported high-level sensor categories."""

    GNSS = "gnss"
    IMU = "imu"
    INS = "ins"
    UNKNOWN = "unknown"


TIMESTAMP_COLUMN = "timestamp"
READABLE_TIME_COLUMN = "readable_time"

GNSS_COLUMNS = [
    "timestamp",
    "readable_time",
    "lat",
    "lon",
    "height",
    "lat_std",
    "lon_std",
    "height_std",
    "position_type",
    "position_type_desc",
    "solution_status",
    "num_sats",
    "num_solution_sats",
]

IMU_COLUMNS = [
    "timestamp",
    "readable_time",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
]

INS_COLUMNS = [
    "timestamp",
    "readable_time",
    "lat",
    "lon",
    "height",
    "roll",
    "pitch",
    "yaw",
    "vel_x",
    "vel_y",
    "vel_z",
    "ins_status",
]

