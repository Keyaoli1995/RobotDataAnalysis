"""ROS2 bag to CSV export helpers."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from robot_data_analysis.ros.flatten import flatten_message_data, safe_topic_filename


def _load_ros2_modules():
    try:
        import rosbag2_py
        from rclpy.serialization import deserialize_message
        from rosidl_runtime_py.utilities import get_message
    except ImportError as exc:
        raise RuntimeError(
            "ROS2 Python packages are required for bag export. "
            "Source your ROS2 environment before using this command."
        ) from exc
    return rosbag2_py, deserialize_message, get_message


def bag_to_csv(bag_path: str | Path, output_dir: str | Path = "csv_output") -> list[Path]:
    """Export every topic in a ROS2 sqlite3 bag to one CSV file per topic."""

    rosbag2_py, deserialize_message, get_message = _load_ros2_modules()
    bag_path = Path(bag_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}
    topic_messages = defaultdict(list)

    while reader.has_next():
        topic, data, timestamp = reader.read_next()
        if topic not in type_map:
            continue

        msg_type_class = get_message(type_map[topic])
        msg = deserialize_message(data, msg_type_class)
        msg_data = flatten_message_data(msg)
        msg_data["timestamp"] = timestamp
        topic_messages[topic].append(msg_data)

    written_files: list[Path] = []
    for topic, messages in topic_messages.items():
        if not messages:
            continue

        csv_path = output_path / f"{safe_topic_filename(topic)}.csv"
        all_fieldnames = set()
        for message in messages:
            all_fieldnames.update(message.keys())
        fieldnames = ["timestamp"] + sorted(field for field in all_fieldnames if field != "timestamp")

        with csv_path.open("w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for message in messages:
                writer.writerow({field: message.get(field, "") for field in fieldnames})

        written_files.append(csv_path)

    return written_files

