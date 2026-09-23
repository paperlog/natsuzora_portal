import json
from datetime import datetime

def update_timetable(schedule_type="None", time_str="", title="", date_str=None):
    """
    時間割JSONを更新する関数
    :param schedule_type: "配信", "動画", "未定", "None" など
    :param time_str: "19:00〜", "21:00" など
    :param title: 配信タイトル（省略時は空文字）
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
                "time": time_str,
                "title": title if schedule_type == "配信" else ""
            }
        ]
    }

    with open("timetable.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    s_type = input("未定 or 配信 or None：").strip()
    s_time = ""
    s_title = ""

    if s_type == "配信":
        s_time = input("開始時刻（例: 20:00〜）：").strip()
        s_title = input("配信タイトル（デフォルトのままで良ければ空Enter）：").strip()
    elif s_type == "動画":
        s_time = input("投稿時刻（例: 18:00）：").strip()

    update_timetable(schedule_type=s_type, time_str=s_time, title=s_title)
    print("timetable.json を更新しました！")
