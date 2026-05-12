import pandas as pd

from robot_data_analysis.io.dataset import scan_csv_files


def test_scan_csv_files_detects_sensor_type_and_basic_metadata(tmp_path):
    gnss = tmp_path / "novatel_oem7_bestgnsspos.csv"
    imu = tmp_path / "imu_data.csv"
    pd.DataFrame({"timestamp": [1], "lat": [39.0]}).to_csv(gnss, index=False)
    pd.DataFrame({"timestamp": [1], "gyro_x": [0.1]}).to_csv(imu, index=False)

    files = scan_csv_files(tmp_path)

    assert [item.name for item in files] == [
        "imu_data.csv",
        "novatel_oem7_bestgnsspos.csv",
    ]
    assert [item.sensor_type for item in files] == ["imu", "gnss"]
    assert files[0].row_count == 1
    assert files[1].columns == ["timestamp", "lat"]

