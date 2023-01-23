"""Команда /history. Получение истории своих запросов (какие команды вызывались от запрашивающего логина)."""

from json import dumps, loads
from logging import getLogger
from typing import Any, Dict

from telebot.types import Message

from config import Config

logger = getLogger(__name__)


def start(message: Message):
    """Начало диалога. Оно же конец - выдача истории запросов по логину.

    :param message: объект сообщения.
    """
    username = message.from_user.username
    logger.debug(dumps(message.json, ensure_ascii=False))
    Config.save_history(username=username, description=message.text)
    with open("history.json", "r", encoding="utf-8") as history_file:
        global_history_obj: Dict[str, Any] = loads(history_file.read())
        user_history = [
            history_item for history_item in global_history_obj["history"]
            if history_item["username"] == username
        ]
    history_view = ""
    for item in user_history:
        history_view += f"[{item['datetime']}] {item['description']}\n"
    msg_txt = f"{Config.get_language_obj(username=username)['messages']['history']['1']}\n\n{history_view}"
    Config.bot.send_message(chat_id=message.from_user.id, text=msg_txt)
