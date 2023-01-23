"""Команда /secondary. Поиск упражнений по указанной вспомогательной мышечной группе."""

from json import dumps
from logging import getLogger

from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logger = getLogger(__name__)


@Config.bot.callback_query_handler(
    func=lambda call: call.message.text == Config.get_language_obj(
        call.from_user.username
    )["messages"]["secondary"]["1"]
)
def select_secondary_muscle_callback(call):
    """Перехватчик события выбора вспомогательной мышечной группы."""
    get_exercises_limit(message=call, secondary_muscle=call.data)


def start(message: Message):
    """Начало диалога. Запрос вспомогательной мышечной группы (выбор из списка).

    :param message: объект сообщения.
    """
    username = message.from_user.username
    logger.debug(dumps(message.json, ensure_ascii=False))
    Config.save_history(username=username, description=message.text)
    msg_txt = Config.get_language_obj(username=username)["messages"]["secondary"]["1"]
    markup = InlineKeyboardMarkup(row_width=1)
    muscles = Config.api_client.get_muscles(language=Config.get_language(username))
    for muscle in muscles:
        btn_muscle = InlineKeyboardButton(
            text=muscle["translate"].capitalize(),
            callback_data=muscle["origin_name"]
        )
        markup.add(btn_muscle)
    Config.bot.send_message(chat_id=message.from_user.id, text=msg_txt, reply_markup=markup)


def get_exercises_limit(message: Message, secondary_muscle: str):
    """Запрос от пользователя максимального размера выдачи.

    :param message: объект сообщения;
    :param secondary_muscle: оригинальное (en) название мышечной группы для запроса к сервису.
    """
    username = message.from_user.username
    lang_obj = Config.get_language_obj(username)
    muscles = Config.api_client.get_muscles(language=Config.get_language(username=username))
    muscle_lang_obj = [muscle for muscle in muscles if muscle["origin_name"] == secondary_muscle][0]
    translated_muscle = muscle_lang_obj['translate'].capitalize()
    msg_text = lang_obj["messages"]["primary"]["2"].format(translated_muscle, secondary_muscle.capitalize())
    bot_q = Config.bot.send_message(chat_id=message.from_user.id, text=msg_text, parse_mode="HTML")
    Config.bot.register_next_step_handler(
        message=bot_q,
        callback=get_exercises_by_secondary_muscle,
        secondary_muscle=secondary_muscle
    )


def get_exercises_by_secondary_muscle(message: Message, secondary_muscle: str):
    """Запрос упражнений у сервиса и отправка серии сообщений (упражнений) пользователю в чат.

    :param message: объект сообщения;
    :param secondary_muscle: оригинальное (en) название мышечной группы для запроса к сервису.
    """
    username = message.from_user.username
    lang_obj = Config.get_language_obj(username)
    if message.text.isdigit() is False:
        Config.bot.send_message(chat_id=message.from_user.id, text=lang_obj["messages"]["primary"]["3"])
        get_exercises_limit(message, secondary_muscle=secondary_muscle)
    else:
        exercises = Config.api_client.search_exercise_by_secondary_muscle(
            secondary_muscle=secondary_muscle,
            language=Config.get_language(username),
            limit=int(message.text)
        )
        if len(exercises) == 0:
            Config.bot.send_message(
                chat_id=message.from_user.id,
                text=lang_obj["messages"]["secondary"]["4"].format(secondary_muscle),
                parse_mode="HTML"
            )
        for exercise in exercises:
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
            exercise_str += (
                f"{lang_obj['obj_field_names'].get('Type', 'Type')}: <b>{exercise['Type'].capitalize()}</b>\n"
            )
            exercise_str += f"{lang_obj['obj_field_names'].get('Workout Type', 'Workout Type')}:\n"
            for workout_type in exercise["Workout Type"]:
                exercise_str += f"  - <b>{workout_type.capitalize()}</b>\n"
            exercise_str += (
                f"{lang_obj['obj_field_names'].get('Youtube link', 'Youtube link')}: "
                f"{exercise['Youtube link']}\n\n"
            )
            Config.bot.send_message(
                chat_id=message.from_user.id,
                text=exercise_str,
                parse_mode="HTML"
            )
        Config.bot.send_message(
            chat_id=message.from_user.id,
            text=lang_obj["messages"]["help_text"],
            parse_mode="HTML"
        )
