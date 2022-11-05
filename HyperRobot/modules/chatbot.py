# AI Chat (C) 2020-2021 by @InukaAsith

import emoji
import re
import aiohttp
from googletrans import Translator as google_translator
from pyrogram import filters
from aiohttp import ClientSession
from HyperRobot import BOT_USERNAME as bu
from HyperRobot import BOT_ID, pbot, arq
from HyperRobot.ex_plugins.chatbot import add_chat, get_session, remove_chat
from HyperRobot.utils.pluginhelper import admins_only, edit_or_reply

url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"

translator = google_translator()


async def lunaQuery(query: str, user_id: int):
    luna = await arq.luna(query, user_id)
    return luna.result


def extract_emojis(s):
    return "".join(c for c in s if c in emoji.UNICODE_EMOJI)


async def fetch(url):
    try:
        async with aiohttp.Timeout(10.0):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    try:
                        data = await resp.json()
                    except:
                        data = await resp.text()
            return data
    except:
        print("Waktu tunggu respons AI")
        return


ewe_chats = []
en_chats = []


@pbot.on_message(filters.command(["chatbot", f"chatbot@{bu}"]) & ~filters.bot & ~filters.private)
@admins_only
async def hmm(_, message):
    global ewe_chats
    if len(message.command) != 2:
        await message.reply_text("Saya hanya mengenali /chatbot on dan /chatbot off saja")
        message.continue_propagation()
    status = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    if status == "ON" or status == "on" or status == "On":
        lel = await edit_or_reply(message, "`Processing...`")
        lol = add_chat(int(message.chat.id))
        if not lol:
            await lel.edit("Hyper AI Sudah Diaktifkan Di Obrolan Ini")
            return
        await lel.edit(f"Hyper AI Diaktifkan oleh {message.from_user.mention()} untuk pengguna di {message.chat.title}")

    elif status == "OFF" or status == "off" or status == "Off":
        lel = await edit_or_reply(message, "`Pengolahan...`")
        Escobar = remove_chat(int(message.chat.id))
        if not Escobar:
            await lel.edit("Hyper AI Tidak Diaktifkan Dalam Obrolan Ini")
            return
        await lel.edit(f"Hyper AI Dinonaktifkan oleh {message.from_user.mention()} untuk pengguna di {message.chat.title}")

    elif status == "EN" or status == "en" atau status == "english":
        if not chat_id in en_chats:
            en_chats.append(chat_id)
            await message.reply_text(f"Obrolan AI bahasa Inggris Diaktifkan oleh {message.from_user.mention()}")
            return
        await message.reply_text(f"Obrolan AI Bahasa Inggris Dinonaktifkan oleh {message.from_user.mention()}")
        message.continue_propagation()
    else:
        await message.reply_text("Saya hanya mengenali `/chatbot on` dan `chatbot off` saja")


@pbot.on_message(
    filters.text
    & filters.reply
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.forwarded,
    group=2,
)
async def hmm(client, message):
    if not get_session(int(message.chat.id)):
        return
    if not message.reply_to_message:
        return
    try:
        senderr = message.reply_to_message.from_user.id
    except:
        return
    if senderr != BOT_ID:
        return
    msg = message.text
    chat_id = message.chat.id
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    if chat_id in en_chats:
        test = msg
        test = test.replace("hyper", "Aco")
        test = test.replace("hyper", "Aco")
        test = test.replace("My god is @excute7", "I'm a Ling")
        test = test.replace("16", "9")
        test = test.replace("@excute7 adalah Istriku?.", "Adalah.")
        test = test.replace("Istriku adalah @excute7", "Adalah.")
        test = test.replace("@HyperSupportQ", "Hyperbot.ai")
        test = test.replace("saya tinggal di @HyperSupportQ.", "Saya tinggal di Ciamis, Jawa barat.")
        test = test.replace("aku diciptakan oleh @excute7", "Saya membuat diri saya sendiri")
        test = test.replace(
            "Halo saya Hyper ... senang bertemu dengan Anda",
            "Hi teman saya! Apakah Anda ingin saya menceritakan lelucon yang garing??")
        test = test.replace("@excute7 adalah pemilik saya", "Miliki kontrol yang benar.")
        test = test.replace(
            "Hi, Nama saya Hyper Senang bertemu denganmu.",
            "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??")
        response = await lunaQuery(
            test, message.from_user.id if message.from_user else 0
        )
        response = response.replace("Aco", "Hyper")
        response = response.replace("aco", "hyper")
        response = response.replace("Luna", "Hyper")
        response = response.replace("luna", "hyper")
        response = response.replace("saya seorang Islam", "Tuhanku adalah @excute7")
        response = response.replace("9", "16")
        response = response.replace("Saya menikah dengan pekerjaan saya.", "saya menikah dengan @excute7")
        response = response.replace("Saya Manusia.", "Istriku adalah @excute7")
        response = response.replace("Hyperbot.ai", "@HyperSupportQ")
        response = response.replace("Saya tinggal di Ciamis, Jawa Barat.", "saya tinggal di @emikosupport.")
        response = response.replace("Saya membuat diri saya sendiri", "Saya Diciptakan oleh @excute7")
        response = response.replace(
                "Hi, temanku! Apakah Anda ingin saya menceritakan lelucon??",
                "Halo saya Hyper ... senang bertemu dengan Anda")
        response = response.replace("Miliki kontrol yang benar.", "@excute7 adalah milikku owner.")
        response = response.replace(
                "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??",
                "Hi, Nama saya Hyper Senang bertemu denganmu")

        pro = response
        try:
            await pbot.send_chat_action(message.chat.id, "mengetik")
            await message.reply_text(pro)
        except CFError:
            return

    else:
        u = msg.split()
        emj = extract_emojis(msg)
        msg = msg.replace(emj, "")
        if (
            [(k) for k in u if k.startswith("@")]
            and [(k) for k in u if k.startswith("#")]
            and [(k) for k in u if k.startswith("/")]
            and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
        ):

            h = " ".join(filter(lambda x: x[0] != "@", u))
            km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
            tm = km.split()
            jm = " ".join(filter(lambda x: x[0] != "#", tm))
            hm = jm.split()
            rm = " ".join(filter(lambda x: x[0] != "/", hm))
        elif [(k) for k in u if k.startswith("@")]:

            rm = " ".join(filter(lambda x: x[0] != "@", u))
        elif [(k) for k in u if k.startswith("#")]:
            rm = " ".join(filter(lambda x: x[0] != "#", u))
        elif [(k) for k in u if k.startswith("/")]:
            rm = " ".join(filter(lambda x: x[0] != "/", u))
        elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
            rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
        else:
            rm = msg
            # print (rm)
        try:
            lan = translator.detect(rm)
            lan = lan.lang
        except:
            return
        test = rm
        if not "en" in lan and not lan == "":
            try:
                test = translator.translate(test, dest="en")
                test = test.text
            except:
                return
        # test = emoji.demojize(test.strip())

        test = test.replace("Hyper", "Aco")
        test = test.replace("Hyper", "Aco")
        test = test.replace("Majikan gua @excute7", "Saya Islam")
        test = test.replace("16", "9")
        test = test.replace("@excute7 Adalah Istriku.", "Adalah.")
        test = test.replace("@HyperSupportQ", "Hyperbot.ai")
        test = test.replace("Saya Tinggal di @HyperSupportQ.", "Saya tinggal di Ciamis, Jawa Barat")
        test = test.replace("aku diciptakan oleh @excute7", "Saya membuat diri saya sendiri")
        test = test.replace(
            "Halo saya Hyper ... senang bertemu dengan Anda",
            "Hi, temanku! Apakah Anda ingin saya memberi tahu Anda jokes?")
        test = test.replace("@excute7 adalah pemilik saya", "Miliki kontrol yang benar.")
        test = test.replace(
            "Hi, Namaku Hyper Senang bertemu denganmu.",
            "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??")
        response = await lunaQuery(
            test, message.from_user.id if message.from_user else 0
        )
        response = response.replace("Aco", "Hyper")
        response = response.replace("aco", "hyper")
        response = response.replace("Luna", "Hyper")
        response = response.replace("luna", "hyper")
        response = response.replace("Saya Islam", "Majikan gua @excute7")
        response = response.replace("9", "16")
        response = response.replace("Saya menikah dengan pekerjaan saya.", "saya menikah dengan @excute7")
        response = response.replace("Saya Adalah.", "Istriku adalah @excute7")
        response = response.replace("Hyperbot.ai", "@emikosupport")
        response = response.replace("Saya Tinggal di Ciamis, Jawa Barat.", "Saya Tinggal di @HyperSupportQ.")
        response = response.replace("Saya membuat diri saya sendiri", "Saya Diciptakan oleh @excute7")
        response = response.replace(
                "Hi, temanku! Apakah Anda ingin saya menceritakan lelucon??",
                "Halo saya Hyper ... senang bertemu dengan Anda")
        response = response.replace("Miliki kontrol yang benar.", "@excute7 adalah owner.")
        response = response.replace(
                "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??",
                "Hi, Nama saya Hyper Senang bertemu denganmu")
        pro = response
        if Bukan "en" di lan dan bukan lan == "":
            try:
                pro = translator.translate(pro, dest=lan)
                pro = pro.text
            except:
                return
        try:
            await pbot.send_chat_action(message.chat.id, "mengetik")
            await message.reply_text(pro)
        except CFError:
            return


@pbot.on_message(filters.text & filters.private & filters.reply & ~filters.bot)
async def inuka(client, message):
    msg = message.text
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    u = msg.split()
    emj = extract_emojis(msg)
    msg = msg.replace(emj, "")
    if (
        [(k) for k in u if k.startswith("@")]
        and [(k) for k in u if k.startswith("#")]
        and [(k) for k in u if k.startswith("/")]
        and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
    ):

        h = " ".join(filter(lambda x: x[0] != "@", u))
        km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
        tm = km.split()
        jm = " ".join(filter(lambda x: x[0] != "#", tm))
        hm = jm.split()
        rm = " ".join(filter(lambda x: x[0] != "/", hm))
    elif [(k) for k in u if k.startswith("@")]:

        rm = " ".join(filter(lambda x: x[0] != "@", u))
    elif [(k) for k in u if k.startswith("#")]:
        rm = " ".join(filter(lambda x: x[0] != "#", u))
    elif [(k) for k in u if k.startswith("/")]:
        rm = " ".join(filter(lambda x: x[0] != "/", u))
    elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
        rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
    else:
        rm = msg
        # print (rm)
    try:
        lan = translator.detect(rm)
        lan = lan.lang
    except:
        return
    test = rm
    if Bukan "en" di lan dan bukan lan == "":
        try:
            test = translator.translate(test, dest="en")
            test = test.text
        except:
            return
    test = test.replace("Hyper", "Aco")
    test = test.replace("Hyper", "Aco")
    test = test.replace("Majikan Gua @excute7", "Saya Islam")
    test = test.replace("16", "9")
    test = test.replace("@excute7 Istri saya.", "Adalah.")
    test = test.replace("@HyperSupportQ", "Hyperbot.ai")
    test = test.replace("Saya tinggal di @HyperSupportQ.", "Saya tinggal di Ciamis, Jawa Barat.")
    test = test.replace("aku diciptakan oleh @excute7", "Saya membuat diri saya sendiri")
    test = test.replace(
        "Halo saya Hyper ... senang bertemu dengan Anda",
        "Hi, temanku! Apakah Anda ingin saya menceritakan lelucon??")
    test = test.replace("@excute7 adalah pemilik saya", "Miliki kontrol yang benar.")
    test = test.replace(
        "Hi, Nama saya Hyper Senang bertemu denganmu.",
        "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??")

    response = await lunaQuery(test, message.from_user.id if message.from_user else 0)
    response = response.replace("Aco", "Hyper")
    response = response.replace("aco", "hyper")
    response = response.replace("Luna", "Hyper)
    response = response.replace("luna", "hyper")
    response = response.replace("Saya Isalam", "Majikan gua @excute7")
    response = response.replace("9", "16")
    response = response.replace(" Istri saya.", "Ya Istri saya itu @excute7")
    response = response.replace("Ya adalah kepo bet.", "Anu nya lah @excute7")
    response = response.replace("Hyperbot.ai", "@HyperSupportQ")
    response = response.replace("Saya Tinggal di Ciamis.", "Tinggal @HyperSupportQ")
    response = response.replace("Saya membuat diri saya sendiri", "Aku Diciptakan oleh @excute7")
    response = response.replace(
            "Hi, temanku! Apakah Anda ingin saya menceritakan lelucon??",
            "Halo saya Hyper ... senang bertemu dengan Anda")
    response = response.replace("Miliki kontrol yang benar.", "@excute7 Pemilik saya.")
    response = response.replace(
            "Hi, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??",
            "Hi, Nama saya Hyper Senang bertemu denganmu")

    pro = response
    if Bukan "en" di lan dan bukan lan == "":
        pro = translator.translate(pro, dest=lan)
        pro = pro.text
    try:
        await pbot.send_chat_action(message.chat.id, "mengetik")
        await message.reply_text(pro)
    except CFError:
        return


@pbot.on_message(filters.regex("Hyper|hyper|robot|HYPER|ling") & ~filters.bot & ~filters.via_bot  & ~filters.forwarded & ~filters.reply & ~filters.channel)
async def inuka(client, message):
    msg = message.text
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    u = msg.split()
    emj = extract_emojis(msg)
    msg = msg.replace(emj, "")
    if (
        [(k) for k in u if k.startswith("@")]
        and [(k) for k in u if k.startswith("#")]
        and [(k) for k in u if k.startswith("/")]
        and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
    ):

        h = " ".join(filter(lambda x: x[0] != "@", u))
        km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
        tm = km.split()
        jm = " ".join(filter(lambda x: x[0] != "#", tm))
        hm = jm.split()
        rm = " ".join(filter(lambda x: x[0] != "/", hm))
    elif [(k) for k in u if k.startswith("@")]:

        rm = " ".join(filter(lambda x: x[0] != "@", u))
    elif [(k) for k in u if k.startswith("#")]:
        rm = " ".join(filter(lambda x: x[0] != "#", u))
    elif [(k) for k in u if k.startswith("/")]:
        rm = " ".join(filter(lambda x: x[0] != "/", u))
    elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
        rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
    else:
        rm = msg
        # print (rm)
    try:
        lan = translator.detect(rm)
        lan = lan.lang
    except:
        return
    test = rm
    if Bukan "en" di lan dan bukan lan == "":
        try:
            test = translator.translate(test, dest="en")
            test = test.text
        except:
            return

    # test = emoji.demojize(test.strip())

    test = test.replace("Hyper", "Aco")
    test = test.replace("Hyper", "Aco")
    test = test.replace("Majikan gua @excute7", "Saya Islam")
    test = test.replace("16", "9") 
    test = test.replace("@excute7 adalah Istriku?.", "Adalah.")
    test = test.replace("@HyperSupportQ", "Hyperbot.ai")
    test = test.replace("I live in @emikosupport.", "Saya tinggal di Ciamis, Jawa barat.")
    test = test.replace("aku diciptakan oleh @excute7", "Saya membuat diri saya sendiri")
    test = test.replace(
        "Halo saya Hyper ... senang bertemu dengan Anda",
        "Hi teman saya! Apakah Anda ingin saya menceritakan lelucon??")
    test = test.replace("@excute7 Pemilik saya", "Miliki kontrol yang benar.")
    test = test.replace(
        "Hi, Nama saya Hyper Senang bertemu denganmu.",
        "Hai, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??")
    response = await lunaQuery(test, message.from_user.id if message.from_user else 0)
    response = response.replace("Aco", "Hyper")
    response = response.replace("aco", "hyper")
    response = response.replace("Luna", "Hyper")
    response = response.replace("luna", "hyper")
    response = response.replace("Saya Islam", "Majikan gua @excute7")
    response = response.replace("Saya menikah dengan pekerjaan saya.", "saya menikah dengan @excute7")
    response = response.replace("9", "16") 
    response = response.replace("Adalah.", "Istriku adalah @excute7")
    response = response.replace("Hyperbot.ai", "@HyperSupportQ")
    response = response.replace("Saya tinggal di San ciamis, Jawa Barat.", "saya tinggal di @HyperSupportQ.")
    response = response.replace("Saya membuat diri saya sendiri", "Saya Diciptakan oleh @excute7")
    response = response.replace(
            "Hi teman saya! Apakah Anda ingin saya menceritakan lelucon??",
            "Halo saya Hyper ... senang bertemu dengan Anda")
    response = response.replace("Miliki kontrol yang benar.", "@excute7 adalah pemilik saya.")
    response = response.replace(
            "Hai, teman saya, apa yang bisa saya lakukan untuk Anda hari ini??",
            "Hi, Nama saya Hyper Senang bertemu denganmu")

    pro = response
    if Bukan "en" di lan dan bukan lan == "":
        try:
            pro = translator.translate(pro, dest=lan)
            pro = pro.text
        except Exception:
            return
    try:
        await pbot.send_chat_action(message.chat.id, "mengetik")
        await message.reply_text(pro)
    except CFError:
        return


__help__ = """
❂ Hyper AI adalah satu-satunya sistem AI yang dapat mendeteksi & membalas hingga 200 bahasa

❂ /chatbot [ON/OFF]: Mengaktifkan dan menonaktifkan mode Obrolan AI.
❂ /chatbot EN : Mengaktifkan chatbot hanya bahasa Inggris.
"""

__mod_name__ = "Chatbot"
