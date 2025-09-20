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
                    "title_zh": item["title"].get("pretty", ""),
                    "images": [],
                    "tags": [re.sub(r" +", "_", tag["name"]) for tag in item.get("tags", []) if tag["type"] == "tag"],
                    "parody": [re.sub(r" +", "_", x["name"]) for x in item.get("tags", []) if x["type"] == "parody"],
                    "artist": [re.sub(r" +", "_", x["name"]) for x in item.get("tags", []) if x["type"] == "artist"],
                    "character": [re.sub(r" +", "_", x["name"]) for x in item.get("tags", []) if
                                  x["type"] == "character"],

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
        content = f"<h3>{gallery['title_jp']} / {gallery['title_en']}/ {gallery['title_zh']}</h3>\n"
        content += f"<p>标签: {', '.join(gallery['tags'])}</p>\n"
        content += f"<p>系列: {', '.join(gallery['parody'])}</p>\n"
        content += f"<p>人物: {', '.join(gallery['character'])}</p>\n"
        content += f"<p>作者: {', '.join(gallery['artist'])}</p>\n"
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
    CHATID = os.environ.get("CHATID")
    bot = Bot(token=BOTTOKEN)
    mode="w"


    for gallery in result_list:
        if "males only" in gallery.get("tags", []):
            continue
        title_zh = gallery.get("title_zh")
        title_jp = gallery.get("title_jp")
        title_en = gallery.get("title_en")

        tags_text = html.escape(" ".join([f"#{tag}" for tag in gallery.get("tags", [])]))
        parody_text = html.escape(" ".join([f"#{parody}" for parody in gallery.get("parody", [])]))
        artist_text = html.escape(" ".join([f"#{artist}" for artist in gallery.get("artist", [])]))
        character_text = html.escape(" ".join([f"#{character}" for character in gallery.get("character", [])]))

        telegraph_url = html.escape(gallery.get("telegraph", ""))
        nhentai_url = f"https://nhentai.net/g/{gallery.get('id')}"

        text_parts = []

        if title_jp:
            text_parts.append(f"🇯🇵 <b>日语：</b>\n<code>{html.escape(title_jp)}</code>")
        if title_en:
            text_parts.append(f"🇺🇸 <b>英语：</b>\n<code>{html.escape(title_en)}</code>")
        if title_zh:
            text_parts.append(f"🇨🇳 <b>中文：</b>\n<code>{html.escape(title_zh)}</code>")

        # 以下字段不做判断，始终显示

        text_parts.append(f"🏷 <b>标签：</b>\n{tags_text}")
        text_parts.append(f"🎭 <b>系列：</b>\n{parody_text}")
        text_parts.append(f"🎨 <b>作者：</b>\n{artist_text}")
        text_parts.append(f"👤 <b>角色：</b>\n{character_text}")

        text_parts.append(f"📝 <a href=\"{telegraph_url}\">Telegraph</a>")
        text_parts.append(f"🔗 <a href=\"{nhentai_url}\">源链接</a>")

        text = "\n".join(text_parts)

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





















