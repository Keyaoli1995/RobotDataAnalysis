from array import array

from robot_data_analysis.ros.flatten import flatten_message_data, safe_topic_filename


class Vector3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class ImuLikeMessage:
    __slots__ = ("linear_acceleration", "angular_velocity", "samples")

    def __init__(self):
        self.linear_acceleration = Vector3(1.0, 2.0, 3.0)
        self.angular_velocity = Vector3(0.1, 0.2, 0.3)
        self.samples = [Vector3(4.0, 5.0, 6.0), 7.0]


def test_flatten_message_data_expands_nested_slots_and_arrays():
    flattened = flatten_message_data(ImuLikeMessage())

    assert flattened == {
        "linear_acceleration.x": 1.0,
        "linear_acceleration.y": 2.0,
        "linear_acceleration.z": 3.0,
        "angular_velocity.x": 0.1,
        "angular_velocity.y": 0.2,
        "angular_velocity.z": 0.3,
        "samples[0].x": 4.0,
        "samples[0].y": 5.0,
        "samples[0].z": 6.0,
        "samples[1]": 7.0,
    }


def test_flatten_message_data_expands_python_array_values():
    flattened = flatten_message_data({"accel": array("f", [1.0, 2.0, 3.0])})

    assert flattened == {
        "accel[0]": 1.0,
        "accel[1]": 2.0,
        "accel[2]": 3.0,
    }


def test_safe_topic_filename_removes_leading_slashes():
    assert safe_topic_filename("/novatel/oem7/bestgnsspos") == "novatel_oem7_bestgnsspos"
    assert safe_topic_filename("/") == "unknown_topic"
