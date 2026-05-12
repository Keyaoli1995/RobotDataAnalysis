import subprocess
import sys


def test_ros2bag_legacy_script_help_runs_from_file_path():
    result = subprocess.run(
        [sys.executable, "bag_parse/ros2bag_data_parse.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ROS2 bag" in result.stdout

