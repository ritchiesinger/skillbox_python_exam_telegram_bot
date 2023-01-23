"""Настройки приложения и общие вспомогательные инструменты."""

from datetime import datetime
from json import dumps, loads
from typing import Any, Dict, Literal, List, Optional

from telebot import TeleBot


class Config:
    """Статический класс, хранящий в себе настройки приложения (бота) и управляющий ими."""

    bot_token: Optional[str] = None
    api_key: str = "b5e3362d2cmsh19ae73cd82fac1cp184259jsna7dd64812155"
    host: str = "exerciseapi3.p.rapidapi.com"

    bot: Optional[TeleBot] = None
    api_client = None  # нотации нет из-за цикличного импорта с http_clients

    LANGUAGE_FILES: Dict[str, str] = {"ru": "lang_files/russian.json", "en": "lang_files/english.json"}

    default_language: Literal["ru", "en"] = "ru"
    default_lang_obj: Optional[Dict[str, Any]] = None

    users_config_instanses = {}

    @classmethod
    def get_language_obj(cls, username: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """Получение переводов из языкового файла.

        :param username: логин пользователя для которого нужно получить языковой объект;
        :param language: языковой код для получения языкового объекта (приоритетный параметр).
        :return: объект переводов, спарсеный из языкового файла.
        """
        if language is not None:
            with open(cls.LANGUAGE_FILES[language], "r", encoding="utf-8") as lang_file:
                return loads(lang_file.read())
        if username is not None:
            user_config = cls.users_config_instanses.get(username)
            if user_config is not None:
                return user_config.get("lang_obj") or cls.set_language_obj(username, language=cls.default_language)
            else:
                return cls.set_language_obj(username, language=cls.default_language)
        else:
            return cls.default_lang_obj or cls.set_language_obj()

    @classmethod
    def set_language_obj(cls, username: Optional[str] = None, language: Literal["ru", "en"] = "ru"):
        with open(cls.LANGUAGE_FILES[language], "r", encoding="utf-8") as lang_file:
            lang_obj = loads(lang_file.read())
            if username is not None and cls.users_config_instanses.get(username) is not None:
                cls.users_config_instanses[username].update({"lang_obj": lang_obj, "language": language})
            elif username is not None and cls.users_config_instanses.get(username) is None:
                cls.users_config_instanses[username] = {"lang_obj": lang_obj, "language": language}
            else:
                cls.default_lang_obj = lang_obj
            return lang_obj

    @classmethod
    def get_language(cls, username: Optional[str] = None):
        if username is not None and cls.users_config_instanses.get(username) is not None:
            if cls.users_config_instanses[username].get("language") is None:
                cls.users_config_instanses[username]["language"] = cls.default_language
            return cls.users_config_instanses[username]["language"]

    @classmethod
    def init_bot(cls, bot_token):
        cls.bot = TeleBot(token=bot_token)
        cls.init_api()
        cls.get_language_obj()

    @classmethod
    def init_api(cls):
        """Инициализация клиента API."""
        from http_client import APIHelper  # Чтобы избежать цикличного импорта с модулем http_client
        cls.api_client = APIHelper(cls.host, cls.api_key)

    @classmethod
    def save_history(cls, username: str, description: str):
        """Сохранение в истории запросов.

        :param username: имя пользователя;
        :param description: описание действия.
        """
        history = {}
        with open("history.json", "r", encoding="utf-8") as history_file:
            global_history_obj: Dict[str, Any] = loads(history_file.read())
            global_history_obj["history"].append(
                {"datetime": str(datetime.now()), "username": username, "description": description}
            )
            history.update(global_history_obj)
        with open("history.json", "w", encoding="utf-8") as history_file:
            history_file.write(dumps(history, ensure_ascii=False, indent=2))
