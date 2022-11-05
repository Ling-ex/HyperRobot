import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from HyperRobot.events import register
from HyperRobot import telethn as tbot


PHOTO = "https://telegra.ph/file/e9391ab2bea553a805974.jpg"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"**Hai [{event.sender.first_name}](tg://user?id={event.sender.id}), Dewek Hyper Robot.** \n\n"
  TEXT += "⚪ **Gua Aktif** \n\n"
  TEXT += f"⚪ **Tuhan Gua : [ling-zy](https://t.me/excute7)** \n\n"
  TEXT += f"⚪ **Library Version :** `{telever}` \n\n"
  TEXT += f"⚪ **Telethon Version :** `{tlhver}` \n\n"
  TEXT += f"⚪ **Pyrogram Version :** `{pyrover}` \n\n"
  TEXT += "**Bilang makasih dong, masuk yg ada fi button bawah blok ☺️**"
  BUTTON = [[Button.url("ᴄʜᴀɴɴᴇʟ", "https://t.me/storyQi"), Button.url("ꜱᴜᴘᴘᴏʀᴛ", "https://t.me/HyperRobotQ")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
