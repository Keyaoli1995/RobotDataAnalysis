"""Utilities for flattening ROS-like messages."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


def flatten_message_data(msg: Any) -> dict[str, Any]:
    """Recursively flatten a ROS-like message object into a dictionary."""

    data: dict[str, Any] = {}

    if isinstance(msg, Mapping):
        iterator = msg.items()
    elif hasattr(msg, "__slots__"):
        iterator = ((field_name, getattr(msg, field_name)) for field_name in msg.__slots__)
    else:
        return {"value": msg}

    for field_name, field_value in iterator:
        if hasattr(field_value, "__slots__") or isinstance(field_value, Mapping):
            nested_data = flatten_message_data(field_value)
            for nested_key, nested_val in nested_data.items():
                data[f"{field_name}.{nested_key}"] = nested_val
        elif isinstance(field_value, (list, tuple)):
            for index, item in enumerate(field_value):
                if hasattr(item, "__slots__") or isinstance(item, Mapping):
                    nested_data = flatten_message_data(item)
                    for nested_key, nested_val in nested_data.items():
                        data[f"{field_name}[{index}].{nested_key}"] = nested_val
                else:
                    data[f"{field_name}[{index}]"] = item
        else:
            data[str(field_name)] = field_value

    return data


def safe_topic_filename(topic: str) -> str:
    """Convert a ROS topic name into a stable CSV filename stem."""

    clean_name = topic.replace("/", "_").replace("~", "_").lstrip("_")
    clean_name = Path(clean_name).name
    return clean_name or "unknown_topic"

