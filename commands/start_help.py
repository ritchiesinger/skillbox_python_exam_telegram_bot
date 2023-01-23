"""Команда /start и /help. Получение справки по чат-боту."""

from json import dumps
from logging import getLogger

from telebot.types import Message

from config import Config

logger = getLogger(__name__)


def start(message: Message):
    """Начало диалога. Оно же конец - вывод справки по командам.

    :param message: объект сообщения.
    """
    """Перехватчик для команды /help."""
    username = message.from_user.username
    logger.debug(dumps(message.json, ensure_ascii=False))
    Config.save_history(username=username, description=message.text)
    msg_txt = Config.get_language_obj(username=username)["messages"]["help_text"]
    Config.bot.send_message(message.from_user.id, msg_txt)
