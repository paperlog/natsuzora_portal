import json
import mimetypes
import os
import re
from datetime import date
from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")


def get_r2_client():
    """環境変数からR2 (S3互換) クライアントを生成"""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_BASE_URL]):
        raise ValueError(
            "R2の接続設定または公開URLが不足しています。.env ファイルを確認してください。"
        )

    return boto3.client(
        service_name="s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_to_r2(s3_client, local_path: Path, r2_key: str) -> bool:
    """ローカル画像をR2にアップロード"""
    content_type, _ = mimetypes.guess_type(local_path)
    if not content_type:
        content_type = "image/webp" if local_path.suffix.lower() == ".webp" else "application/octet-stream"

    try:
        print(f"☁️  R2へアップロード中: {local_path.name} -> {r2_key} ...")
        s3_client.upload_file(
            str(local_path),
            R2_BUCKET_NAME,
            r2_key,
            ExtraArgs={"ContentType": content_type},
        )
        print("✅ R2アップロード成功！")
        return True
    except (BotoCoreError, ClientError) as e:
        print(f"❌ R2アップロード失敗: {e}")
        return False


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


def resolve_image_path(raw_input: str) -> Path | None:
    """
    ドラッグ＆ドロップ時にターミナルが付与する不要な記号を掃除し、
    ローカルの実ファイルを特定する
    """
    # 1. 前後の空白、引用符 (', ", `) を除去
    clean = raw_input.strip().strip("'\"`")
    
    # 2. Linux / macOS ターミナルでスペースが '\ ' にエスケープされている場合を解除
    clean = clean.replace(r"\ ", " ")

    # 3. パス候補の確認（絶対パス、またはカレントディレクトリ相対）
    direct_path = Path(clean).expanduser()
    if direct_path.is_file():
        return direct_path.resolve()

    # 4. 相対パスやファイル名だけ入力された場合のフォールバック探索
    candidates = [
        Path(clean),
        Path("img/art_room") / clean,
        Path("img/art_room") / direct_path.name,
    ]
    for p in candidates:
        if p.is_file():
            return p.resolve()

    return None


def main():
    file_name = "art.json"
    datas = load_json(file_name)

    print("=== 夏空学園 美術室 ファンアート登録 (R2自動連携) ===")

    # 1. 画像ファイル（ドラッグ＆ドロップ対応）
    image_input = input("画像をターミナルにドラッグ＆ドロップ (またはファイル名入力): ").strip()
    if not image_input:
        print("入力がなかったため中断しました。")
        return 1

    local_file = resolve_image_path(image_input)
    if not local_file:
        print(f"❌ 画像ファイルが見つかりません: {image_input}")
        return 1

    print(f"📁 検出ファイル: {local_file}")

    # R2上のキー（デスクトップなど別の場所にある画像でも、R2上は img/art_room/ファイル名 に統一）
    filename = local_file.name
    r2_key = filename

    # R2へアップロード実行
    try:
        s3_client = get_r2_client()
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    if not upload_to_r2(s3_client, local_file, r2_key):
        print("アップロードに失敗したため、art.json の更新を中断しました。")
        return 1

    # 公開用URLの組み立て
    full_image_url = f"{R2_PUBLIC_BASE_URL}/{r2_key}"

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
        "image": full_image_url,
        "url": url,
        "author": author,
        "date": art_date,
        "comment": comment,
    }

    # 最新作として先頭に追加
    datas.insert(0, new_art)
    write_json(file_name, datas)

    print(f"\n🎉 登録完了: [{art_id}] {author} の作品を追加しました。")
    print(f"🌐 公開画像URL: {full_image_url}")


if __name__ == "__main__":
    main()
