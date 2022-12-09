import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from HyperRobot import DRAGONS as SUDO_USERS
from HyperRobot import pbot
from HyperRobot.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ Bergabunglah dengan kami @{channel} saluran dan tekan 'Suarakan Saya' button.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Anda telah dibisukan oleh admin karena beberapa alasan lain.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} sedang mencoba untuk mengaktifkan suara sendiri tetapi saya tidak dapat mengaktifkannya karena saya bukan admin dalam obrolan ini, tambahkan saya sebagai admin lagi.**\n__#Meninggalkan obrolan ini...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Peringatan! Jangan tekan tombol saat Anda bisa berbicara.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Selamat datang {} 🙏 \n **Anda belum bergabung dengan kami @{} Saluran belum**👷 \n \nTolong ikut [Our Channel](https://t.me/{}) dan tekan **UNMUTE ME** Button. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Bergabunglah dengan Saluran",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "Unmute Me", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **Hyper bukan admin disini..**\n__Memberi saya melarang izin dan coba lagi.. \n#Ending FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"😕 **saya bukan admin @{channel} channel.**\n__Memberi saya admin saluran itu dan coba lagi.\n#Ending FSub...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Paksa Berlangganan Berhasil Dinonaktifkan.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Mengaktifkan semua anggota yang dibisukan oleh saya...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit(
                        "✅ **Suarakan semua anggota yang dibisukan oleh saya.**"
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **Saya bukan admin di chat ini.**\n__Saya tidak dapat mengaktifkan suara anggota karena saya bukan admin dalam obrolan ini, jadikan saya admin dengan izin pengguna larangan.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Paksa Berlangganan is Enabled**\n__Paksa Berlangganan diaktifkan, semua anggota grup harus berlangganan ini [channel](https://t.me/{input_str}) untuk mengirim pesan di grup ini.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"😕 **Bukan Admin di Channel**\n__Saya bukan admin di [channel](https://t.me/{input_str}). Tambahkan saya sebagai admin untuk mengaktifkan ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Nama Pengguna Saluran Tidak Valid.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Paksa Berlangganan diaktifkan di obrolan ini.**\n__Untuk ini [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text(
                    "❌ **Paksa Berlangganan dinonaktifkan dalam obrolan ini.**"
                )
    else:
        message.reply_text(
            "❗ **Diperlukan Pembuat Grup**\n__Anda harus menjadi pembuat grup untuk melakukan itu.__"
        )


__help__ = """
*Force Subscribe:*
❂ Hyper dapat membisukan anggota yang tidak berlangganan saluran Anda sampai mereka berlangganan
❂ Saat diaktifkan, saya akan membisukan anggota yang tidak berlangganan dan menunjukkan kepada mereka tombol suarakan. Ketika mereka menekan tombol, saya akan membunyikan mereka
❂*Mempersiapkan*
*Hanya pencipta*
❂ Tambahkan saya di grup Anda sebagai admin
❂ Tambahkan saya di saluran Anda sebagai admin 
 
*Commmands*
❂ /fsub {channel username} - Untuk mengaktifkan dan mengatur saluran.
  💡Lakukan ini dulu...
❂ /fsub - Untuk mendapatkan pengaturan saat ini.
❂ /fsub disable - Untuk mematikan ForceSubscribe..
  💡Jika Anda menonaktifkan fsub, Anda perlu mengatur lagi agar berfungsi.. /fsub {channel username} 
❂ /fsub clear - Untuk membunyikan semua anggota yang dibisukan oleh saya.
*Federasi*
Semuanya menyenangkan, sampai spammer mulai memasuki grup Anda, dan Anda harus memblokirnya. Maka Anda harus mulai melarang lebih banyak, dan lebih banyak lagi, dan itu menyakitkan.
Tetapi kemudian Anda memiliki banyak grup, dan Anda tidak mau .\n
*Perintah:*\n
FBI sekarang dibagi menjadi 3 bagian untuk kemudahan Anda.
• `/fedownerhelp`*:* Memberikan bantuan untuk pembuatan makan dan perintah khusus pemilik
• `/fedadminhelp`*:* Memberikan bantuan untuk perintah administrasi makan
• `/feduserhelp`*:* Memberikan bantuan untuk perintah yang dapat digunakan siapa saja
"""
__mod_name__ = "F-Sub/Feds"
