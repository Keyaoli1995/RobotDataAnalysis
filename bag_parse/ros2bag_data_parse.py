#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robot_data_analysis.ros.bag_exporter import bag_to_csv
from robot_data_analysis.ros.flatten import flatten_message_data as extract_message_data

def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description='将ROS2 bag文件转换为CSV格式')
    parser.add_argument('bag_path', help='ROS2 bag文件路径')
    parser.add_argument('-o', '--output', default='csv_output',
                       help='输出目录 (默认: csv_output)')

    args = parser.parse_args()

    if not os.path.exists(args.bag_path):
        print(f"错误: bag文件路径不存在: {args.bag_path}")
        return

    print(f"输入bag文件: {args.bag_path}")
    print(f"输出目录: {args.output}")
    print("-" * 50)

    written_files = bag_to_csv(args.bag_path, args.output)
    print(f"\n转换完成！生成 {len(written_files)} 个CSV文件，保存到: {args.output}")

if __name__ == "__main__":
    main()
