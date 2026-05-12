# Robot Data Analysis Library Design

## Goal

Build an offline robot experiment data analysis library. The library should load ROS2 bag exports or existing CSV files, normalize multi-sensor data into stable pandas DataFrame schemas, run basic quality and timing analysis, and generate reusable outputs for later plotting and reports.

## Current Context

The project currently contains two scripts:

- `bag_parse/ros2bag_data_parse.py`: reads ROS2 bag files, flattens ROS messages, and writes one CSV per topic.
- `bag_parse/parse_bestgnsspos.py`: reads a NovAtel `bestgnsspos` CSV and extracts useful GNSS fields.

The first version should preserve these capabilities while moving reusable logic into a package named `robot_data_analysis`.

## Scope

The first version supports offline analysis of one experiment directory. It will focus on CSV-based analysis first, because ROS2 bag reading depends on a ROS runtime that may not exist inside a general conda data analysis environment.

The first version includes:

- A package layout for future GNSS, IMU, and INS analysis.
- A ROS message flattening utility.
- A CSV dataset scanner.
- Standard DataFrame schema conventions for GNSS, IMU, and INS.
- A complete NovAtel `bestgnsspos` parser.
- Basic quality summaries: row count, time range, sampling rate, null counts, and duplicate timestamps.
- A CLI entry point for dataset summary and `bestgnsspos` parsing.
- Compatibility wrappers for the existing scripts.

The first version does not include advanced sensor fusion, map rendering, real-time processing, or ROS2 runtime installation.

## Architecture

The package is split by responsibility:

- `core`: shared schemas, time helpers, and quality summaries.
- `io`: CSV and experiment directory loading.
- `ros`: ROS message flattening and ROS2 bag export helpers.
- `sensors`: sensor-specific parsers and metrics.
- `analysis`: cross-sensor analysis such as quality and time synchronization.
- `visualization`: plotting helpers added incrementally after stable schemas exist.
- `cli`: command-line commands that call package APIs.

The CLI should stay thin. Reusable logic belongs in importable modules so notebooks, tests, and future automation can call the same APIs.

## Data Flow

```text
ROS2 bag or exported CSV directory
    -> dataset scanner
    -> sensor parser
    -> standardized pandas DataFrame
    -> quality/time analysis
    -> cleaned CSV, summaries, plots, or reports
```

## Standard Schemas

GNSS normalized columns:

```text
timestamp, readable_time, lat, lon, height,
lat_std, lon_std, height_std,
position_type, solution_status, num_sats, num_solution_sats
```

IMU normalized columns:

```text
timestamp, readable_time,
accel_x, accel_y, accel_z,
gyro_x, gyro_y, gyro_z
```

INS normalized columns:

```text
timestamp, readable_time,
lat, lon, height,
roll, pitch, yaw,
vel_x, vel_y, vel_z,
ins_status
```

Parsers may keep extra source columns when useful, but analysis modules should rely on the standard names.

## Error Handling

Library functions should raise typed exceptions for missing files, missing required columns, and invalid timestamps. CLI commands should catch these exceptions and print concise user-facing errors.

Parser functions should return DataFrames, not strings. This keeps errors explicit and prevents downstream code from accidentally treating an error message as data.

## Testing

The first version should use pytest. Tests should cover pure Python behavior without requiring ROS2:

- ROS message flattening with fake slot-based objects.
- NovAtel `bestgnsspos` normalization from a small CSV fixture.
- Dataset scanning and quality summaries.
- CLI smoke tests where practical.

ROS2 bag export should remain import-safe when ROS2 packages are unavailable. Runtime ROS2 errors should only happen when a caller explicitly uses the ROS bag exporter without ROS installed.

## Git Strategy

Initialize this directory as a Git repository. Commit the design and plan first, then commit the first package implementation after verification.

