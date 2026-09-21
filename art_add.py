import json
import re
from datetime import date
from pathlib import Path


def load_json(file_name: str) -> list[dict[str, str]]:
    path = Path(file_name)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_name: str, datas: list[dict[str, str]]) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False, indent=2)


def generate_next_id(datas: list[dict[str, str]]) -> str:
    """既存の art-XXX から最大番号を探して次のIDを採番"""
    max_num = 0
    for item in datas:
        match = re.search(r"art-(\d+)", item.get("id", ""))
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"art-{max_num + 1:03d}"


def extract_author_from_url(url: str) -> str:
    """XのURLから @ユーザー名 を抽出"""
    match = re.search(r"(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)", url)
    return f"@{match.group(1)}" if match else ""


def main():
    file_name = "art.json"
    datas = load_json(file_name)

    print("=== 夏空学園 美術室 ファンアート登録 ===")

    # 1. 画像ファイル名 / パス
    image_input = input("画像ファイル名 (例: sample.webp): ").strip()
    if not image_input:
        print("画像ファイル名が未入力のため中断しました。")
        return 1

    # パス整形（img/art_room/ が含まれていなければ自動付与）
    if not image_input.startswith("img/art_room/"):
        image_path = f"img/art_room/{image_input}"
    else:
        image_path = image_input

    # 2. XのポストURL
    url = input("XのポストURL: ").strip()

    # 3. 作者名（URLから抽出した値をデフォルト提示）
    default_author = extract_author_from_url(url)
    author_prompt = (
        f"作者名 (Enterで '{default_author}'): " if default_author else "作者名: "
    )
    author = input(author_prompt).strip()
    if not author and default_author:
        author = default_author

    # 4. 日付（今日の日付をデフォルト提示）
    today = date.today().isoformat()
    date_input = input(f"日付 (Enterで '{today}'): ").strip()
    art_date = date_input if date_input else today

    # 5. コメント（任意）
    comment = input("コメント (省略可): ").strip()

    # データ組み立て
    art_id = generate_next_id(datas)
    new_art = {
        "id": art_id,
        "image": image_path,
        "url": url,
        "author": author,
        "date": art_date,
        "comment": comment,
    }

    # 最新作として先頭に追加
    datas.insert(0, new_art)
    write_json(file_name, datas)

    print(f"\n✅ 登録完了: [{art_id}] {author} の作品を art.json の先頭に追加しました。")


if __name__ == "__main__":
    main()
