import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robot_data_analysis.sensors.gnss.novatel import parse_bestgnsspos_csv

def parse_novatel_bestgnsspos(file_path):
    return parse_bestgnsspos_csv(file_path)


if __name__ == "__main__":
    # 使用示例
    file_name = '/home/keyaoli/Data/TimeSync/实机测试/1/rosbag2_2026_03_18-14_43_01/csv_output/novatel_oem7_bestgnsspos.csv'
    data = parse_novatel_bestgnsspos(file_name)

    # 打印前5行查看结果
    print("解析后的关键数据：")
    print(data.head())

    # 如果你想保存成一个新的干净的 Excel 或 CSV
    # data.to_csv('cleaned_gnss_pos.csv', index=False)
