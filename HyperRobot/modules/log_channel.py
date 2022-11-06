from datetime import datetime
from functools import wraps
from telegram.ext import CallbackContext
from HyperRobot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import ParseMode, Update
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, JobQueue, run_async
    from telegram.utils.helpers import escape_markdown

    from HyperRobot import EVENT_LOGS, LOGGER, dispatcher
    from HyperRobot.modules.helper_funcs.chat_status import user_admin
    from HyperRobot.modules.sql import log_channel_sql as sql

    def loggable(func):
        @wraps(func)
        def log_action(
            update: Update,
            context: CallbackContext,
            job_queue: JobQueue = None,
            *args,
            **kwargs,
        ):
            if not job_queue:
                result = func(update, context, *args, **kwargs)
            else:
                result = func(update, context, job_queue, *args, **kwargs)

            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += f"\n<b>Event Stamp</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">click here</a>'
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return log_action

    def gloggable(func):
        @wraps(func)
        def glog_action(update: Update, context: CallbackContext, *args, **kwargs):
            result = func(update, context, *args, **kwargs)
            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += "\n<b>Event Stamp</b>: <code>{}</code>".format(
                    datetime.utcnow().strftime(datetime_fmt)
                )

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">click here</a>'
                log_chat = str(EVENT_LOGS)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return glog_action

    def send_log(
        context: CallbackContext, log_chat_id: str, orig_chat_id: str, result: str
    ):
        bot = context.bot
        try:
            bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message == "Chat not found":
                bot.send_message(
                    orig_chat_id, "Saluran log ini telah dihapus - tidak disetel."
                )
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Could not parse")

                bot.send_message(
                    log_chat_id,
                    result
                    + "\n\nPemformatan telah dinonaktifkan karena kesalahan yang tidak terduga.",
                )

    @user_admin
    def logging(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                f"Grup ini memiliki semua log yang dikirim ke:"
                f" {escape_markdown(log_channel_info.title)} (`{log_channel}`)",
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            message.reply_text("Tidak ada saluran log yang disetel untuk grup ini!")

    @user_admin
    def setlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat
        if chat.type == chat.CHANNEL:
            message.reply_text(
                "Sekarang, teruskan /setlog ke grup tempat Anda ingin mengikat saluran ini!"
            )

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Pesan untuk dihapus tidak ditemukan":
                    pass
                else:
                    LOGGER.exception(
                        "Kesalahan menghapus pesan di saluran log. Bagaimanapun juga harus bekerja."
                    )

            try:
                bot.send_message(
                    message.forward_from_chat.id,
                    f"Saluran ini telah ditetapkan sebagai saluran log untuk {chat.title or chat.first_name}.",
                )
            except Unauthorized as excp:
                if excp.message == "Forbidden: bot bukan anggota obrolan saluran":
                    bot.send_message(chat.id, "Berhasil mengatur saluran log!")
                else:
                    LOGGER.exception("KESALAHAN dalam mengatur saluran log.")

            bot.send_message(chat.id, "Berhasil mengatur saluran log!")

        else:
            message.reply_text(
                "Langkah-langkah untuk mengatur saluran log adalah:\n"
                " - tambahkan bot ke saluran yang diinginkan\n"
                " - Kirim /setlog ke saluran\n"
                " - meneruskan /setlog ke grup\n"
            )

    @user_admin
    def unsetlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(
                log_channel, f"Saluran telah dibatalkan tautannya dari {chat.title}"
            )
            message.reply_text("Saluran log telah tidak disetel.")

        else:
            message.reply_text("Belum ada saluran log yang disetel!")

    def __stats__():
        return f"× {sql.num_logchannels()} saluran log diatur."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return f"Grup ini memiliki semua log yang dikirim ke: {escape_markdown(log_channel_info.title)} (`{log_channel}`)"
        return "Tidak ada saluran log yang disetel untuk grup ini!"


    __help__ = """
──「 Log channel 」──

❂ /logchannel*:* dapatkan info saluran log
❂ /setlog*:* atur saluran log.
❂ /unsetlog*:* hapus saluran log.

*Pengaturan saluran log dilakukan dengan*:

➩ menambahkan bot ke saluran yang diinginkan (sebagai admin!)
➩ mengirim /setlog di saluran
➩ penerusan the /setlog ke grup
"""

    __mod_name__ = "Log Channel​"

    LOG_HANDLER = CommandHandler("logchannel", logging, run_async=True)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog, run_async=True)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog, run_async=True)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func

    def gloggable(func):
        return func
