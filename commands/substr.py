"""Команда /substr. Поиск упражнений по подстроке."""

from json import dumps
from logging import getLogger

from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logger = getLogger(__name__)


@Config.bot.callback_query_handler(
    func=lambda call: call.message.text == Config.get_language_obj(call.from_user.username)["messages"]["substr"]["2"]
)
def select_exercise_name_callback(call):
    """Перехватчик события выбора варианта упражнения из саджестера."""
    get_exercise_by_name(message=call, exercise_name=call.data)


def start(message: Message):
    """Начало диалога. Запрос подстроки на основании которой будет поиск.

    :param message: объект сообщения.
    """
    username = message.from_user.username
    logger.debug(dumps(message.json, ensure_ascii=False))
    Config.save_history(username=username, description=message.text)
    msg_text = Config.get_language_obj(username)["messages"]["substr"]["1"]
    bot_q = Config.bot.send_message(chat_id=message.from_user.id, text=msg_text, parse_mode="HTML")
    Config.bot.register_next_step_handler(message=bot_q, callback=get_suggest)


def get_suggest(message: Message):
    """Начало диалога. Получение уточнений.

    :param message: объект сообщения.
    """
    username = message.from_user.username
    search_q = message.text
    suggested_items = {
        exercise_origin_name: translated_name
        for exercise_origin_name, translated_name in Config.get_language_obj(username=username)["exercise_name"].items()
        if translated_name.lower().find(search_q.lower()) != -1
    }
    if len(suggested_items) > 0:
        msg_txt = Config.get_language_obj(username=username)["messages"]["substr"]["2"]
        markup = InlineKeyboardMarkup(row_width=1)
        for exercise_origin_name, translated_name in suggested_items.items():
            btn_muscle = InlineKeyboardButton(
                text=translated_name.capitalize(),
                callback_data=exercise_origin_name
            )
            markup.add(btn_muscle)
        Config.bot.send_message(chat_id=message.from_user.id, text=msg_txt, reply_markup=markup)
    else:
        msg_txt = Config.get_language_obj(username=username)["messages"]["substr"]["3"]
        Config.bot.send_message(chat_id=message.from_user.id, text=msg_txt)


def get_exercise_by_name(message: Message, exercise_name: str):
    """Запрос данных по упражнению в сервис по указанному названию упражнения.

    :param message: объект сообщения;
    :param exercise_name: оригинальное (en) название упражнения.
    """
    username = message.from_user.username
    lang_obj = Config.get_language_obj(username=username)
    exercise = Config.api_client.search_exercise_by_name(name=exercise_name, language=Config.get_language(username))
    exercise_str = (
        f"<b>{exercise['Name'].capitalize()}</b>\n\n"
        f"{lang_obj['obj_field_names'].get('Force', 'Force')}: <b>{exercise['Force'].capitalize()}</b>\n"
        f"{lang_obj['obj_field_names'].get('Primary Muscles', 'Primary Muscles')}:\n"
    )
    for muscle in exercise["Primary Muscles"]:
        exercise_str += f"  - <b>{muscle.capitalize()}</b>\n"
    exercise_str += f"{lang_obj['obj_field_names'].get('SecondaryMuscles', 'SecondaryMuscles')}:\n"
    for muscle in exercise["SecondaryMuscles"]:
        exercise_str += f"  - <b>{muscle.capitalize()}</b>\n"
    exercise_str += f"{lang_obj['obj_field_names'].get('Type', 'Type')}: <b>{exercise['Type'].capitalize()}</b>\n"
    exercise_str += f"{lang_obj['obj_field_names'].get('Workout Type', 'Workout Type')}:\n"
    for workout_type in exercise["Workout Type"]:
        exercise_str += f"  - <b>{workout_type.capitalize()}</b>\n"
    exercise_str += (
        f"{lang_obj['obj_field_names'].get('Youtube link', 'Youtube link')}: {exercise['Youtube link']}\n\n"
    )
    Config.bot.send_message(chat_id=message.from_user.id, text=exercise_str, parse_mode="HTML")
    Config.bot.send_message(chat_id=message.from_user.id, text=lang_obj["messages"]["help_text"], parse_mode="HTML")
