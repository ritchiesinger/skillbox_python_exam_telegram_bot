"""Команда /lang. Смена языка приложения."""

from json import dumps
from logging import getLogger

from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logger = getLogger(__name__)


@Config.bot.callback_query_handler(
    func=lambda call: call.message.text == Config.get_language_obj(call.from_user.username)["messages"]["lang"]["1"]
)
def select_lang_callback(call):
    """Перехватчик события выбора языка."""
    logger.debug(dumps(call.json, ensure_ascii=False))
    username = call.from_user.username
    Config.set_language_obj(username=username, language=call.data)
    msg_txt = Config.get_language_obj(username=username)["messages"]["help_text"]
    Config.bot.send_message(chat_id=call.message.chat.id, text=msg_txt)


def start(message: Message):
    """Начало диалога. Запрос языка (выбор из списка).

    :param message: объект сообщения.
    """
    username = message.from_user.username
    logger.debug(dumps(message.json, ensure_ascii=False))
    Config.save_history(username=username, description=message.text)
    msg_txt = Config.get_language_obj(username=username)["messages"]["lang"]["1"]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru"),
        InlineKeyboardButton(text="English 🇬🇧", callback_data="en")
    )
    Config.bot.send_message(chat_id=message.from_user.id, text=msg_txt, reply_markup=markup)
