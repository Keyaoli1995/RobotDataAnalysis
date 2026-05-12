import json
from pathlib import Path

from scripts.run_export_bag import ExportBagConfig, build_worker_shell_command, load_config, main


def test_load_config_reads_bag_and_output_paths(tmp_path):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(
        json.dumps(
            {
                "bag_path": "/data/run/rosbag2_2026_01_01",
                "output_dir": "/data/run/csv_output",
                "ros_setup": "/opt/ros/humble/setup.bash",
                "workspace_setup": "/home/keyaoli/ros2_ws/install/setup.bash",
                "python_executable": "/usr/bin/python3",
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config == ExportBagConfig(
        bag_path=Path("/data/run/rosbag2_2026_01_01"),
        output_dir=Path("/data/run/csv_output"),
        ros_setup=Path("/opt/ros/humble/setup.bash"),
        workspace_setup=Path("/home/keyaoli/ros2_ws/install/setup.bash"),
        python_executable=Path("/usr/bin/python3"),
    )


def test_load_config_rejects_missing_required_keys(tmp_path):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(json.dumps({"bag_path": "/data/run"}), encoding="utf-8")

    try:
        load_config(config_path)
    except ValueError as exc:
        assert "output_dir" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing output_dir")


def test_load_config_defaults_to_system_python_for_ros(tmp_path):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(
        json.dumps(
            {
                "bag_path": "/data/run/rosbag2_2026_01_01",
                "output_dir": "/data/run/csv_output",
                "workspace_setup": "/home/keyaoli/ros2_ws/install/setup.bash",
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.ros_setup == Path("/opt/ros/humble/setup.bash")
    assert config.workspace_setup == Path("/home/keyaoli/ros2_ws/install/setup.bash")
    assert config.python_executable == Path("/usr/bin/python3")



def test_build_worker_shell_command_sources_ros_setups_before_python(tmp_path):
    config_path = tmp_path / "local_run.json"
    script_path = Path("/repo/scripts/run_export_bag.py")
    config = ExportBagConfig(
        bag_path=Path("/data/run/rosbag2_2026_01_01"),
        output_dir=Path("/data/run/csv_output"),
        ros_setup=Path("/opt/ros/humble/setup.bash"),
        workspace_setup=Path("/home/keyaoli/ros2_ws/install/setup.bash"),
        python_executable=Path("/usr/bin/python3"),
    )

    command = build_worker_shell_command(config, config_path, script_path)

    assert "source /opt/ros/humble/setup.bash" in command
    assert "source /home/keyaoli/ros2_ws/install/setup.bash" in command
    assert "/usr/bin/python3 /repo/scripts/run_export_bag.py --worker --config" in command


def test_main_reports_config_errors_without_traceback(tmp_path, capsys):
    config_path = tmp_path / "local_run.json"
    config_path.write_text(json.dumps({"bag_path": "/data/run"}), encoding="utf-8")

    exit_code = main(["--config", str(config_path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "ERROR: missing required config keys" in captured.err
    assert "Traceback" not in captured.err
