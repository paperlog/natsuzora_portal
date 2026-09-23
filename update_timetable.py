import json
from datetime import datetime

def update_timetable(schedule_type="None", time_str="", date_str=None):
    """
    時間割JSONを更新する関数
    :param schedule_type: "配信", "動画", "None" など
    :param time_str: "19:00〜", "21:00" など（Noneの場合は空文字でOK）
    :param date_str: "9/25" 形式。省略時は当日の日付
    """
    if not date_str:
        now = datetime.now()
        date_str = f"{now.month}/{now.day}"

    data = {
        "date": date_str,
        "items": [
            {
                "type": schedule_type,
                "time": time_str
            }
        ]
    }

    with open("timetable.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__=="__main__":
    update_timetable(schedule_type=input("未定 or 配信 or None："), time_str=input("開始時刻："))

# --- 使い方例 ---
# 1. 今日の配信をセットする場合
# update_timetable(schedule_type="配信", time_str="19:00〜")

# 2. 今日をお休みにする場合
# update_timetable(schedule_type="None")
