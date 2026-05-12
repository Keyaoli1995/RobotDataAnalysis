"""Command-line interface for robot_data_analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from robot_data_analysis.analysis.quality import summarize_dataframe
from robot_data_analysis.io.csv import read_csv, write_csv
from robot_data_analysis.io.dataset import scan_csv_files
from robot_data_analysis.ros.bag_exporter import bag_to_csv
from robot_data_analysis.sensors.gnss.novatel import parse_bestgnsspos_csv


def _cmd_summary(args: argparse.Namespace) -> int:
    root = Path(args.path)
    files = scan_csv_files(root)
    result = []
    for item in files:
        df = read_csv(item.path)
        summary = summarize_dataframe(df)
        result.append(
            {
                "name": item.name,
                "path": str(item.path),
                "sensor_type": item.sensor_type,
                "summary": summary,
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cmd_parse_bestgnsspos(args: argparse.Namespace) -> int:
    parsed = parse_bestgnsspos_csv(args.csv_path)
    if args.output:
        destination = write_csv(parsed, args.output)
        print(f"wrote {destination}")
    else:
        print(parsed.head().to_string(index=False))
    return 0


def _cmd_export_bag(args: argparse.Namespace) -> int:
    written_files = bag_to_csv(args.bag_path, args.output)
    for path in written_files:
        print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline robot experiment data analysis tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="summarize CSV files in an experiment directory")
    summary.add_argument("path", help="experiment directory containing CSV files")
    summary.set_defaults(func=_cmd_summary)

    parse_gnss = subparsers.add_parser("parse-bestgnsspos", help="normalize a NovAtel BESTGNSSPOS CSV")
    parse_gnss.add_argument("csv_path", help="source BESTGNSSPOS CSV")
    parse_gnss.add_argument("-o", "--output", help="optional output CSV path")
    parse_gnss.set_defaults(func=_cmd_parse_bestgnsspos)

    export_bag = subparsers.add_parser("export-bag", help="export a ROS2 bag to topic CSV files")
    export_bag.add_argument("bag_path", help="ROS2 bag directory path")
    export_bag.add_argument("-o", "--output", default="csv_output", help="output directory")
    export_bag.set_defaults(func=_cmd_export_bag)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

