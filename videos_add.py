import json
import re

def get_id(url:str) -> str:
    match=re.search(r"/video/(\d+)", url)
    video_id=match.group(1) if match else ""
    return video_id

def load_json(file_name:str) -> list[dict[str, str]]:
    with open(file_name,"r",encoding="utf-8") as f:
        datas=json.load(f)
    return datas

def write_json(file_name:str, datas:list[dict[str, str]]) -> None:
    with open(file_name,"w",encoding="utf-8") as f:
        json.dump(datas,f,ensure_ascii=False,indent=2)

def main():
    file_name="videos.json"
    datas=load_json(file_name)
    title=input("タイトルを入力してください:")
    url=input("urlを入力してください:")
    if not title or not url:
        print("書き込みしませんでした")
        return 1
    id=get_id(url)
    data={"id":id, "title":title, "url":url}
    datas.insert(1,data)
    write_json(file_name,datas)
    print("書き込みが完了しました")

if __name__=="__main__":
    main()
