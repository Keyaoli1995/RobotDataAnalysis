from pathlib import Path


def test_legacy_bag_parse_directory_is_removed_from_main_project_layout():
    assert not Path("bag_parse").exists()

