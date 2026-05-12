# Robot Data Analysis

Offline data analysis utilities for robot experiment logs.

The first version focuses on loading ROS2 bag topic CSV exports, normalizing sensor data into pandas DataFrames, and producing basic quality summaries. ROS2 bag export remains available as a lazy optional path because it requires ROS2 Python packages such as `rosbag2_py` and `rclpy`.

## Quick Start

```bash
conda activate data_analysis
python -m robot_data_analysis.cli.main --help
python -m robot_data_analysis.cli.main summary path/to/experiment_dir
python -m robot_data_analysis.cli.main parse-bestgnsspos path/to/novatel_oem7_bestgnsspos.csv -o cleaned_gnss.csv
```

## Package Layout

```text
robot_data_analysis/
  core/          shared schemas, errors, and time helpers
  io/            CSV and experiment directory loading
  ros/           ROS message flattening and bag export helpers
  sensors/       GNSS, IMU, INS parser locations
  analysis/      quality and future cross-sensor analysis
  visualization/ future plotting helpers
  cli/           command-line entry points
```

## Testing

The local ROS installation exposes pytest plugins that may not be compatible with the conda Python version. Disable third-party pytest plugin autoloading when running this project's tests:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 conda run -n data_analysis python -m pytest tests -q
```

