import pandas as pd

from robot_data_analysis.sensors.gnss.novatel import parse_bestgnsspos_csv


def test_parse_bestgnsspos_csv_normalizes_standard_columns(tmp_path):
    source = tmp_path / "novatel_oem7_bestgnsspos.csv"
    pd.DataFrame(
        {
            "_timestamp": [1_700_000_000_000_000_000],
            "lat": [39.1],
            "lon": [116.2],
            "hgt": [50.3],
            "lat_stdev": [0.1],
            "lon_stdev": [0.2],
            "hgt_stdev": [0.3],
            "pos_type.type": [51],
            "sol_status.status": [0],
            "num_svs": [20],
            "num_sol_svs": [18],
        }
    ).to_csv(source, index=False)

    parsed = parse_bestgnsspos_csv(source)

    assert list(parsed.columns) == [
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
    assert parsed.loc[0, "height"] == 50.3
    assert parsed.loc[0, "position_type_desc"] == "NARROW_INT"
    assert str(parsed.loc[0, "readable_time"]) == "2023-11-14 22:13:20"


def test_parse_bestgnsspos_csv_raises_for_missing_columns(tmp_path):
    source = tmp_path / "bad.csv"
    pd.DataFrame({"timestamp": [1]}).to_csv(source, index=False)

    try:
        parse_bestgnsspos_csv(source)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
        assert "lat" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing columns")

