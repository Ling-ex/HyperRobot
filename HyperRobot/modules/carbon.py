from platform import python_version as y
from telegram import __version__ as o
from pyrogram import __version__ as z
from telethon import __version__ as s
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from HyperRobot import pbot
from HyperRobot.utils.errors import capture_err
from HyperRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`Membalas pesan teks untuk membuat karbon.`")
    if not message.reply_to_message.text:
        return await message.reply_text("`Membalas pesan teks untuk membuat karbon.`")
    m = await message.reply_text("`Mempersiapkan Karbon`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`Mengunggah`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


MEMEK = "https://telegra.ph/file/e9391ab2bea553a805974.jpg"

@pbot.on_message(filters.command("repo"))
async def repo(_, message):
    await message.reply_photo(
        photo=MEMEK,
        caption=f"""✨ **Hey I'm Hyper Robot** 

**Owner repo : [ling-ex](https://t.me/excute7)**
**Python Version :** `{y()}`
**Library Version :** `{o}`
**Telethon Version :** `{s}`
**Pyrogram Version :** `{z}`

**Buat sendiri dengan klik tombol di bawah.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "repo", url="https://t.me/HyperSupportQ"), 
                    InlineKeyboardButton(
                        "Channel", url="https://t.me/storyQi")
                ]
            ]
        )
    )
