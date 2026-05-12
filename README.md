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

## IDE Run Script

For click-to-run usage in VS Code or another IDE, copy the example local config and edit the paths:

```bash
cp configs/local_run.example.json configs/local_run.json
```

Then open and run:

```text
scripts/run_export_bag.py
```

The script runs as a launcher first: it sources the configured ROS setup files,
then starts a worker Python process that performs the bag export. This keeps ROS
Python packages and custom message packages available before `rosbag2_py` is
imported.

Config fields:

```json
{
  "bag_path": "/home/keyaoli/Data/example/rosbag2_2026_01_01-00_00_00",
  "output_dir": "/home/keyaoli/Data/example/rosbag2_2026_01_01-00_00_00/csv_output",
  "ros_setup": "/opt/ros/humble/setup.bash",
  "workspace_setup": "/home/keyaoli/ros2_ws/install/setup.bash",
  "python_executable": "/usr/bin/python3"
}
```

`configs/local_run.json` is ignored by Git so local data paths stay on your machine.
`workspace_setup` should point to the `install/setup.bash` for the workspace
that contains custom message packages used by your bag, such as `robot_msgs` or
`novatel_oem7_msgs`.

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
