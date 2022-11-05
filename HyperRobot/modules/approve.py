import html
from HyperRobot.modules.disable import DisableAbleCommandHandler
from HyperRobot import dispatcher, DRAGONS
from HyperRobot.modules.helper_funcs.extraction import extract_user
from telegram.ext import CallbackContext, CallbackQueryHandler
import HyperRobot.modules.sql.approve_sql as sql
from HyperRobot.modules.helper_funcs.chat_status import user_admin
from HyperRobot.modules.log_channel import loggable
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest


@loggable
@user_admin
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Saya tidak tahu siapa yang Anda bicarakan, Replay dulu bego TOLOL🗿!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text(
            "Pengguna sudah admin - locks, blocklists, dan anti banjir sudah tidak berlaku. Agak laen.",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) sudah disetujui di {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) telah disetujui di {chat_title}! Mereka sekarang akan diabaikan oleh tindakan admin otomatis seperti locks, blocklists, dan antiflood.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Saya tidak tahu siapa yang Anda bicarakan, Replay dulu TOLOL🗿!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text("Pengguna ini adalah admin, mereka tidak dapat ditolak kecuali di bunuh hhe.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} belum disetujui!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} tidak lagi disetujui di, mampus lo🤣 {chat_title}.",
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "Pengguna berikut disetujui.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"Tidak ada pengguna yang disetujui tolol di {chat_title}.")
        return ""
    message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "Siapa yang mau lu approve tolol, ya minimal replay dulu tolol😅!",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} adalah pengguna yang disetujui. Locks, antiflood, and blocklists tidak akan berlaku untuk mereka.",
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} bukan pengguna yang disetujui. Mereka dipengaruhi oleh perintah normal.",
        )


def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Hanya pemilik obrolan yang dapat membatalkan persetujuan semua pengguna sekaligus, emng lu own nya🗿.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users",
                        callback_data="unapproveall_user",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data="unapproveall_cancel",
                    ),
                ],
            ],
        )
        update.effective_message.reply_text(
            f"Apakah Anda yakin ingin membatalkan persetujuan SEMUA pengguna di {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            message.edit_text("Successfully Unapproved all user in this Chat.")
            return

        if member.status == "administrator":
            query.answer("Hanya pemilik obrolan yang dapat melakukan ini.")

        if member.status == "member":
            query.answer("Anda harus menjadi admin untuk melakukan ini haha so soan.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("Penghapusan semua pengguna yang disetujui telah dibatalkan.")
            return ""
        if member.status == "administrator":
            query.answer("Hanya pemilik obrolan yang dapat melakukan ini, bukan own mah diam aja om/tante.")
        if member.status == "member":
            query.answer("Anda harus menjadi admin untuk melakukan ini haha so soan.")


__help__ = """
Terkadang, Anda mungkin memercayai pengguna untuk tidak mengirim konten yang tidak diinginkan.
Mungkin tidak cukup untuk menjadikannya admin, tetapi Anda mungkin baik-baik saja dengan locks, blacklists, and antiflood tidak berlaku untuk mereka.

Untuk itulah persetujuan - setujui pengguna yang dapat dipercaya untuk memungkinkan mereka mengirim

*Perintah admin:*
❂ /approval*:* Periksa status persetujuan pengguna di obrolan ini.
❂ /approve*:* Menyetujui pengguna. Locks, blacklists, dan antiflood tidak akan berlaku untuk mereka lagi.
❂ /unapprove*:* Tidak menyetujui pengguna. Mereka sekarang akan tunduk pada locks, blacklists, dan antiflood lagi.
❂ /approved*:* Daftar semua pengguna yang disetujui.
❂ /unapproveall*:* Batalkan persetujuan *SEMUA* pengguna dalam obrolan. Ini tidak dapat dibatalkan.
"""

APPROVE = DisableAbleCommandHandler("approve", approve, run_async=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, run_async=True)
APPROVED = DisableAbleCommandHandler("approved", approved, run_async=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, run_async=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall, run_async=True)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*", run_async=True
)

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Approvals"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
