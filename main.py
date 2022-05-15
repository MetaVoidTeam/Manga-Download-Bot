from pyrogram import Client, filters
from pyrogram.types import *
import random
import json
import img2pdf
from metaapi import META
import requests
import aiohttp
import asyncio

import os
import re

API_ID = os.environ.get("API_ID", None) 
API_HASH = os.environ.get("API_HASH", None) 
BOT_TOKEN = os.environ.get("BOT_TOKEN", None) 


bot = Client(
    "KukiBot" ,
    api_id = API_ID,
    api_hash = API_HASH ,
    bot_token = BOT_TOKEN
)

def call_back_filter(data):
    return filters.create(lambda flt, _, query: flt.data in query.data,
                          data=data)


@bot.on_callback_query(call_back_filter("mangaid"))
def mangaid_callback(_, query):
    mangaid = query.data.split(":")[2]

    n= META()
    manga = f"{mangaid}"
    y = n.manga_detail(manga)
    data = y['chapters']
    m = []
    for x in data:
        m.append(f"{x['chapternumber']}")
    query.message.edit(f'Chapter Number - {m}\n /mangadownload {mangaid} chapterno', parse_mode='markdown')


@bot.on_message(
    filters.command("mangasearch", prefixes=["/", ".", "?", "-"]))
async def manga(client, message):
        search = message.command[1]
        limit = "12"
        n = META()
        mangasearch = f"{search}"
        y = n.manga_search(mangasearch, limit)
        keyb = []
        for x in y:
            keyb.append([InlineKeyboardButton(f"{x['title']}", callback_data=f"mangaid:mangaid:{x['mangaid']}")])
        repl = InlineKeyboardMarkup(keyb)
        await message.reply_text(f"Your Search Results for **{mangasearch}**", reply_markup=repl, parse_mode="markdown")




@bot.on_message(
    filters.command("mangadownload", prefixes=["/", ".", "?", "-"]))
async def manga(client, message):
        manga = message.command[1]
        chapter = message.command[2]

        n= META()

        mangaid = f"{manga}"
   
        chap = f"{chapter}"

        y = n.mangadl(mangaid, chap)

        k = 1
        os.mkdir(mangaid)
        for x in y:
            img = x['img']
            src = requests.get(img).content
            with open(f"{mangaid}/{k}.jpg" , "wb") as f:
                f.write(src)
            k += 1
            filepaths = []
            for root, directories, files in os.walk(f"{mangaid}"):
               for name in files:
                    mangafile = os.path.join(root, name)
                    filepaths.append(mangafile)

            filepaths.sort(key=lambda f: int(re.sub('\D', '', f)))
            with open(f"{mangaid}-chapter-{chap}.pdf" ,"wb") as f:
                 f.write(img2pdf.convert(filepaths))
        await bot.send_document(message.chat.id , f"{mangaid}-chapter-{chap}.pdf")
        os.remove(f"{mangaid}-chapter-{chap}.pdf")
        os.system(f"rm -rf {mangaid}")


bot.run()
