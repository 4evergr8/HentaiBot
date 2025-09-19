import html
import os
import re
import time
import requests
from telegraph import Telegraph
import asyncio
from telegram import Bot


async def main():
    def fetch_nhentai(config, result_list):
        for page in range(1, 3):
            url = f"https://nhentai.net/api/galleries/search?query=chinese&page={page}&sort=new-uploads"
            response = requests.get(url)
            data = response.json()


            for item in data.get("result", []):
                gid = str(item["id"])
                print(gid)

                if gid in config:
                    return result_list # 直接返回，结束函数

                media_id = item["media_id"]
                gallery_dict = {
                    "id": gid,
                    "title_jp": item["title"].get("japanese", ""),
                    "title_en": item["title"].get("english", ""),
                    "images": [],
                    "tags": [re.sub(r" +", "_", tag["name"]) for tag in item.get("tags", [])]
                }

                for index, page in enumerate(item["images"]["pages"], start=1):
                    t = page.get("t", "j")
                    ext = {"j": "jpg", "p": "png", "g": "gif", "w": "webp"}.get(t, "jpg")
                    page_url = f"https://i.nhentai.net/galleries/{media_id}/{index}.{ext}"
                    gallery_dict["images"].append(page_url)

                result_list.append(gallery_dict)


        return result_list

    with open("data/record", "r", encoding="utf-8") as f:
        config = [line.strip() for line in f if line.strip()]
    print(config)




    result_list = []
    result_list =fetch_nhentai(config, result_list)
    result_list.reverse()
    print(result_list)










    telegraph = Telegraph()
    telegraph.create_account(short_name='hentai_bot')


    for gallery in result_list:
        content = f"<h3>{gallery['title_jp']} / {gallery['title_en']}</h3>\n"
        content += f"<p>标签: {', '.join(gallery['tags'])}</p>\n"
        for img_url in gallery['images']:
            content += f'<img src="{img_url}"><br>\n'
        response = telegraph.create_page(
            title=gallery['title_jp'] or gallery['title_en'],
            html_content=content
        )
        #print(response["url"])
        gallery["telegraph"] = response["url"]
        time.sleep(5)






    BOTTOKEN = os.environ.get("BOTTOKEN")
    CHATID =    os.environ.get("CHATID")
    bot = Bot(token=BOTTOKEN)
    mode="w"


    for gallery in result_list:
        title = gallery["title_jp"] or gallery["title_en"]
        title = html.escape(title)
        tags_text = html.escape(" ".join([f"#{tag}" for tag in gallery["tags"]]))
        telegraph_url = html.escape(gallery["telegraph"])
        text = f'<b>标题：</b> <a href="{telegraph_url}">{title}</a>\n<b>标签：</b> {tags_text}\n<b>Telegraph：</b> {telegraph_url}'


        await bot.send_message(
            chat_id=CHATID,
            text=text,
            parse_mode="HTML"
        )


        with open("data/record", mode, encoding="utf-8") as f:
            f.write(str(gallery["id"]) + "\n")
        mode = "a"  # 只有写入成功才切换
        await asyncio.sleep(10)










if __name__ == "__main__":
    asyncio.run(main())





















