import html
from typing import Optional

import HyperRobot.modules.sql.blsticker_sql as sql
from HyperRobot import LOGGER, dispatcher
from HyperRobot.modules.connection import connected
from HyperRobot.modules.disable import DisableAbleCommandHandler
from HyperRobot.modules.helper_funcs.alternate import send_message
from HyperRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from HyperRobot.modules.helper_funcs.misc import split_message
from HyperRobot.modules.helper_funcs.string_handling import extract_time

from HyperRobot.modules.log_channel import loggable
from HyperRobot.modules.warns import warn
from telegram import Chat, Message, ParseMode, Update, User, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html, mention_markdown


def blackliststicker(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    sticker_list = "<b>Daftar stiker yang masuk daftar hitam saat ini {}:</b>\n".format(
        chat_name,
    )

    all_stickerlist = sql.get_chat_stickers(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_stickerlist:
            sticker_list += "<code>{}</code>\n".format(html.escape(trigger))
    elif len(args) == 0:
        for trigger in all_stickerlist:
            sticker_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(sticker_list)
    for text in split_text:
        if (
            sticker_list
            == "<b>Daftar stiker yang masuk daftar hitam saat ini {}:</b>\n".format(
                chat_name,
            ).format(html.escape(chat_name))
        ):
            send_message(
                update.effective_message,
                "Tidak ada stiker daftar hitam di <b>{}</b>!".format(
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
            return
    send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
def add_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )

        added = 0
        for trigger in to_blacklist:
            try:
                get = bot.getStickerSet(trigger)
                sql.add_to_stickers(chat_id, trigger.lower())
                added += 1
            except BadRequest:
                send_message(
                    update.effective_message,
                    "Sticker `{}` tidak dapat ditemukan!".format(trigger),
                    parse_mode="markdown",
                )

        if added == 0:
            return

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "Sticker <code>{}</code> ditambahkan ke stiker daftar hitam di <b>{}</b>!".format(
                    html.escape(to_blacklist[0]),
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "<code>{}</code> stiker ditambahkan ke stiker daftar hitam di <b>{}</b>!".format(
                    added,
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        added = 0
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "Stiker tidak valid!")
            return
        try:
            get = bot.getStickerSet(trigger)
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1
        except BadRequest:
            send_message(
                update.effective_message,
                "Sticker `{}` tidak dapat ditemukan!".format(trigger),
                parse_mode="markdown",
            )

        if added == 0:
            return

        send_message(
            update.effective_message,
            "Sticker <code>{}</code> ditambahkan ke stiker daftar hitam di <b>{}</b>!".format(
                trigger,
                html.escape(chat_name),
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        send_message(
            update.effective_message,
            "Beri tahu saya stiker apa yang ingin Anda tambahkan ke daftar hitam.",
        )


@user_admin
def unblackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_unblacklist = list(
            {trigger.strip() for triggers in text.split("\n") if trigger.strip()},
        )

        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_stickers(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "Sticker <code>{}</code> dihapus dari daftar hitam di <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]),
                        html.escape(chat_name),
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message,
                    "Stiker ini tidak ada dalam daftar hitam...!",
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "Sticker <code>{}</code> dihapus dari daftar hitam di <b>{}</b>!".format(
                    successful,
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "Tak satu pun dari stiker ini ada, jadi tidak bisa dilepas.",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "Sticker <code>{}</code> dihapus dari daftar hitam. {} tidak ada, jadi tidak dihapus.".format(
                    successful,
                    len(to_unblacklist) - successful,
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "Stiker tidak valid!")
            return
        success = sql.rm_from_stickers(chat_id, trigger.lower())

        if success:
            send_message(
                update.effective_message,
                "Sticker <code>{}</code> dihapus dari daftar hitam di <b>{}</b>!".format(
                    trigger,
                    chat_name,
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "{} tidak ditemukan di stiker daftar hitam...!".format(trigger),
            )
    else:
        send_message(
            update.effective_message,
            "Beri tahu saya stiker apa yang ingin Anda tambahkan ke daftar hitam.",
        )


@loggable
@user_admin
def blacklist_mode(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "Anda dapat melakukan perintah ini dalam grup, bukan PM tolol",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "turn off"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "kiri, pesan akan dihapus"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "diperingatkan"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "meredam"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ditendang"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "dilarang"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """Sepertinya Anda mencoba menetapkan nilai sementara ke daftar hitam, tetapi belum menentukan waktunya; menggunakan `/blstickermode tban <timevalue>`.
                                              Contoh nilai waktu: 4m = 4 minute, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "dilarang sementara untuk {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """Sepertinya Anda mencoba menetapkan nilai sementara ke daftar hitam, tetapi belum menentukan waktunya; menggunakan `/blstickermode tmute <timevalue>`.
                                              Contoh nilai waktu: 4m = 4 minute, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "dibungkam sementara untuk {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "Saya hanya mengerti off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return
        if conn:
            text = "Mode stiker daftar hitam berubah, pengguna akan `{}` at *{}*!".format(
                settypeblacklist,
                chat_name,
            )
        else:
            text = "Mode stiker daftar hitam berubah, pengguna akan `{}`!".format(
                settypeblacklist,
            )
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>Admin:</b> {}\n"
            "Mengubah mode daftar hitam stiker. pengguna akan {}.".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    getmode, getvalue = sql.get_blacklist_setting(chat.id)
    if getmode == 0:
        settypeblacklist = "tidak aktif"
    elif getmode == 1:
        settypeblacklist = "menghapus"
    elif getmode == 2:
        settypeblacklist = "memperingatkan"
    elif getmode == 3:
        settypeblacklist = "bisu"
    elif getmode == 4:
        settypeblacklist = "tendangan"
    elif getmode == 5:
        settypeblacklist = "melarang"
    elif getmode == 6:
        settypeblacklist = "dilarang sementara untuk {}".format(getvalue)
    elif getmode == 7:
        settypeblacklist = "dibungkam sementara untuk {}".format(getvalue)
    if conn:
        text = "Mode stiker daftar hitam saat ini disetel ke *{}* in *{}*.".format(
            settypeblacklist,
            chat_name,
        )
    else:
        text = "Mode stiker daftar hitam saat ini disetel ke *{}*.".format(
            settypeblacklist,
        )
    send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


@user_not_admin
def del_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user
    to_match = message.sticker
    if not to_match or not to_match.set_name:
        return
    bot = context.bot
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_stickers(chat.id)
    for trigger in chat_filters:
        if to_match.set_name.lower() == trigger.lower():
            try:
                if getmode == 0:
                    return
                if getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        "Menggunakan stiker '{}' yang di blacklist stiker".format(
                            trigger,
                        ),
                        message,
                        update.effective_user,
                        # conn=False,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        "{} dibisukan karena menggunakan '{}' yang di blacklist stiker".format(
                            mention_markdown(user.id, user.first_name),
                            trigger,
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            "{} ditendang karena menggunakan '{}' yang di blacklist stiker".format(
                                mention_markdown(user.id, user.first_name),
                                trigger,
                            ),
                            parse_mode="markdown",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.kick_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        "{} dilarang karena menggunakan '{}' yang di blacklist stiker".format(
                            mention_markdown(user.id, user.first_name),
                            trigger,
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.kick_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        "{} dilarang untuk {} karena menggunakan '{}' yang di blacklist stiker".format(
                            mention_markdown(user.id, user.first_name),
                            value,
                            trigger,
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=mutetime,
                    )
                    bot.sendMessage(
                        chat.id,
                        "{} dibisukan untuk {} karena menggunakan '{}' yang di blacklist stiker".format(
                            mention_markdown(user.id, user.first_name),
                            value,
                            trigger,
                        ),
                        parse_mode="markdown",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Pesan untuk dihapus tidak ditemukan":
                    LOGGER.exception("Kesalahan saat menghapus pesan daftar hitam.")
                break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("sticker_blacklist", {})
    for trigger in blacklist:
        sql.add_to_stickers(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_stickers_chat_filters(chat_id)
    return "Ada `{} `blacklisted stickers.".format(blacklisted)


def __stats__():
    return "× {} stiker daftar hitam, di seluruh {} obrolan.".format(
        sql.num_stickers_filters(),
        sql.num_stickers_filter_chats(),
    )


__mod_name__ = "Stiker Daftar Hitam"

BLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "blsticker",
    blackliststicker,
    admin_ok=True,
    run_async=True,
)
ADDBLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "addblsticker",
    add_blackliststicker,
    run_async=True,
)
UNBLACKLIST_STICKER_HANDLER = CommandHandler(
    ["unblsticker", "rmblsticker"],
    unblackliststicker,
    run_async=True,
)
BLACKLISTMODE_HANDLER = CommandHandler("blstickermode", blacklist_mode)
BLACKLIST_STICKER_DEL_HANDLER = MessageHandler(
    Filters.sticker & Filters.chat_type.groups,
    del_blackliststicker,
    run_async=True,
)

dispatcher.add_handler(BLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(ADDBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(UNBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_STICKER_DEL_HANDLER)
