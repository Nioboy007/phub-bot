import asyncio
import os
import youtube_dl
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram import Client, filters
from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pyrogram import Client, filters
from pyrogram.errors.exceptions import UserNotParticipant
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQuery,
                            InlineQueryResultArticle, InputTextMessageContent,
                            Message)
from youtube_dl.utils import DownloadError

from config import *
from helpers import download_progress_hook
from pyrogram import filters



SUDO = int(SUDO)
APP_ID = APP_ID
APP_HASH = APP_HASH
BOT_TOKEN = BOT_TOKEN
MUST_JOIN = MUST_JOIN
app = Client("pornhub_bot",
            api_id=APP_ID,
            api_hash=APP_HASH,
            bot_token=BOT_TOKEN)

if os.path.exists("downloads"):
    print("Unduhan Sudah Ada")
else:
    print("Unduhan Telah Dibuat")

btn1 = InlineKeyboardButton("Tap To Search 🤤",switch_inline_query_current_chat="",)
btn2 = InlineKeyboardButton("Search In A Group💦", switch_inline_query="")

active_list = []
queue = []


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def link_fil(filter, client, update):
    if "www.pornhub" in update.text:
        return True
    else:
        return False

link_filter = filters.create(link_fil, name="link_filter")


@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    if not MUST_JOIN:  # Bukan member channel
        return
    try:
        try:
            await bot.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await bot.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"You must join our channel first.\n\n[click here]({link}) to join our channel before your..........💦🤭.\n\nAfter joining, please type /start again!",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✨ Join Our Channel✨", url=link)]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"I'm not admin in the MUST_JOIN chat : {MUST_JOIN} !")

@app.on_inline_query()
async def search(client, InlineQuery : InlineQuery):
    query = InlineQuery.query
    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    results = []
    try:
        src = await api.search.search(query)#, ordering="mostviewed")
    except ValueError as e:
        results.append(InlineQueryResultArticle(
                title="Video Not Found!",
                description="Sorry! Video not found. Try Again!!",
                input_message_content=InputTextMessageContent(
                    message_text="Video Not Found!"
                )
            ))
        await InlineQuery.answer(results,
                            switch_pm_text="Results",
                            switch_pm_parameter="start")
            
        return


    videos = src.videos
    await backend.close()
    

    for vid in videos:

        try:
            pornstars = ", ".join(v for v in vid.pornstars)
            categories = ", ".join(v for v in vid.categories)
            tags = ", #".join(v for v in vid.tags)
        except:
            pornstars = "N/A"
            categories = "N/A"
            tags = "N/A"
        msgg = (f"**TITLE** : `{vid.title}`\n"
                f"**DURATION** : `{vid.duration}`\n"
                f"**VIEWES** : `{vid.views}`\n"
                f"**{pornstars}**\n"
                f"Kategori : {categories}\n\n"
                f"{tags}"
                f"Link : {vid.url}")
	    
        msg = f"{vid.url}"
         
        results.append(InlineQueryResultArticle(
            title=vid.title,
            input_message_content=InputTextMessageContent(
                message_text=msg,
            ),
            description = f"Duration: {vid.duration}\nNumber of Viewers: {vid.views}\nVideo Rating: {vid.rating}",
            thumb_url = vid.thumb,
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("Watch on Website", url=vid.url),
                btn1
            ]]),
        ))

    await InlineQuery.answer(results,
                            switch_pm_text="Search Results",
                            switch_pm_parameter="start")

# Memulai Bot‌‌
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    value = str(message.chat.id)
    with open("member.txt", "a+") as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have those newlines
        if value in lines:
            print(f"user {value} lagi make bot")
        else:
            file.write(value + "\n")
    await message.reply(f"𓂺Hai @{message.from_user.username},\n"
                        "━━━━━━━━━━━━━━━\n"
                        "Iam Here To Fulfill Your Ambitious Mind😻\n"
                        "━━━━━━━━━━━━━━━\n"
                        "- BEWARE Of 🔞, Use Me on your own risk\n"
                        "- Spam Me, I sperm you😤\n"
                        "- Not For Minors 🧒❌\n"
                        "- Not Meant to promote Pornography.\n"
                        "- This is just a bot from crowd requests.\n"
                        "━━━━━━━━━━━━━━━\n\n"
                        "Let's Join the @botio_devs Channel\n\n"
                        "Note: Select a short video so that the download process can be faster💨!!!\n\n\n"
                        "Click the button below to 🔎 :", reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))
    

@app.on_message(link_filter)
async def options(client, message : Message):
    print(message.text)
    await message.reply("What do you want to do?", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Download", f"d_{message.text}"), InlineKeyboardButton("Watch on the web",url=message.text)]
            ])
            )


@app.on_callback_query(filters.regex("^d"))
async def download_video(client, callback : CallbackQuery):
    url = callback.data.split("_",1)[1]
    msg = await callback.message.edit("Downloading.........🥵")
    user_id = callback.message.from_user.id

    if "isjwhs" in active_list:
        await callback.message.edit("Sorry, you can only download videos at a time!🙁")
        return
    else:
        active_list.append(user_id)

    ydl_opts = {
            "progress_hooks": [lambda d: download_progress_hook(d, callback.message, client)]
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            await run_async(ydl.download, [url])
        except DownloadError:
            await callback.message.edit("Sorry, something went wrong...")
            return


    for file in os.listdir('.'):
        if file.endswith(".mp4"):
            await callback.message.reply_video(f"{file}", caption="**This is the video you asked**\n\nBot by:- @botio_devs.",
                                reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))
            os.remove(f"{file}")
            break
        else:
            continue

    await msg.delete()
    active_list.remove(user_id)


@app.on_message(filters.command("cc"))
async def list_files(client, message : Message):
    files = os.listdir("downloads")
    await message.reply(files)

@app.on_message(filters.command("stats") & filters.user(SUDO))
async def botsatats(_, message):
    users = open("member.txt").readlines()
    user = open("member.txt").read()
    total = len(users)
    await message.reply_text(f"Total : {total} Users")
    await message.reply_text(f"{user}")

# Fitur broadcastttt
@app.on_message(filters.command('bcast') & filters.user(SUDO))
async def broadcast(_, message):
    if message.reply_to_message :
        await message.reply_text("Start a Broadcast")
        query = open("member.txt").readlines()
        for row in query:
           try: 
            reply = message.reply_to_message
            await reply.copy(row)
           except:
            pass
            


app.run()
