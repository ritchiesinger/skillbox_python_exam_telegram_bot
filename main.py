"""Telegram-бот для получения данных из ExerciseAPI.

Имя бота: skillbox_python_final_exam

Модуль содержит инициализацию бота и перехватчики для команд.
"""

from argparse import ArgumentParser
from json import dumps
from logging import getLogger, Formatter, FileHandler, DEBUG

from config import Config

parser = ArgumentParser(
    prog="Exercises Telegram Bot",
    description="Telegram-бот для получения данных данных из ExerciseAPI"
)
parser.add_argument('--bot-token', type=str, required=True)
args = parser.parse_args()
Config.init_bot(bot_token=args.bot_token)

# В командах используется Config, поэтому импортировать их надо после инициализации.
from commands import primary, secondary, lang, history, start_help, substr

COMMANDS = ["/help", "/lang", "/primary", "/history", "/secondary", "/substr"]

logger = getLogger()
logger.setLevel(DEBUG)
handler = FileHandler("log.log", mode="w", encoding="utf-8")
formatter = Formatter("[%(name)s][%(asctime)s][%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@Config.bot.message_handler(commands=["help", "start"])
def help_command_handle(message):
    """Перехватчик для команды /help."""
    start_help.start(message)


@Config.bot.message_handler(commands=["lang"])
def lang_command_handle(message):
    """Перехватчик для команды /lang."""
    lang.start(message)


@Config.bot.message_handler(commands=["primary"])
def primary_command_handle(message):
    """Перехватчик для команды /primary."""
    primary.start(message)


@Config.bot.message_handler(commands=["secondary"])
def secondary_command_handle(message):
    """Перехватчик для команды /secondary."""
    secondary.start(message)


@Config.bot.message_handler(commands=["substr"])
def substr_command_handle(message):
    """Перехватчик для команды /substr."""
    substr.start(message)


@Config.bot.message_handler(commands=["history"])
def history_command_handle(message):
    """Перехватчик для команды /history."""
    history.start(message)


@Config.bot.message_handler(content_types=['text'])
def non_commands_message_handle(message):
    """Перехватчик для всех остальных сообщений кроме команд."""
    if message.text not in COMMANDS:
        logger.debug(dumps(message.json, ensure_ascii=False))
        username = message.from_user.username
        Config.save_history(username=username, description=message.text)
        msg_txt = Config.get_language_obj(username=username)["messages"]["parse_error"]
        Config.bot.send_message(message.from_user.id, msg_txt)


Config.bot.polling(none_stop=True, interval=0)
