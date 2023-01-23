"""HTTP-клиент для работы с ExerciseAPI."""

from logging import getLogger
from typing import Any, Dict, Literal, List, Optional

from requests import Session, Response, Request

from config import Config

logger = getLogger(__name__)


class ExerciseAPIClient:
    """HTTP-клиент для работы с ExerciseAPI."""

    def __init__(self, host: str, api_key: str):
        """HTTP-клиент для работы с API Hotels.com.

        :param host: хост API;
        :param api_key: ключ для доступа к API.
        """
        self.endpoint = f"https://{host}"
        self.api_key = api_key
        self.session = Session()
        self.session.headers.update({"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": host})

    def _send_request(self, url: str, params: Optional[Dict[str, str]] = None) -> Response:
        """Отправка запроса.

        :param url: адрес запроса;
        :param params: параметры запроса, передаваемые в URL.
        :return: объект ответа сервиса.
        """
        request = self.session.prepare_request(Request(method="GET", url=url, params=params))
        log_str = f"{request.method} {request.url}\nHeaders: {request.headers}\nParams: {params}"
        logger.debug(log_str)
        response = self.session.send(request)
        logger.debug(response.json())
        return response

    def get_muscles(self) -> Response:
        """Получение списка всех доступных мышечных групп.

        :return: объект ответа сервиса.
        """
        return self._send_request(url=f"{self.endpoint}/search/muscles/")

    def search_exercise_by_name(self, name: str) -> Response:
        """Получение информации об упражнении по переданному названию.

        :param name: название упражнения.
        :return: объект ответа сервиса.
        """
        return self._send_request(url=f"{self.endpoint}/search/", params={"name": name})

    def search_exercise_by_primary_muscle(self, primary_muscle: str) -> Response:
        """Получение списка упражнений по указанной основной мышечной группе.

        :param primary_muscle: основная мышечная группа.
        :return: объект ответа сервиса.
        """
        return self._send_request(url=f"{self.endpoint}/search/", params={"primaryMuscle": primary_muscle})

    def search_exercise_by_secondary_muscle(self, secondary_muscle: str) -> Response:
        """Получение списка упражнений по указанной вспомогательной мышечной группе.

        :param secondary_muscle: вспомогательная мышечная группа.
        :return: объект ответа сервиса.
        """
        return self._send_request(url=f"{self.endpoint}/search/", params={"secondaryMuscle": secondary_muscle})


class APIHelper:
    """Высокоуровневый клиент. Предоставляет возможность работы с API в удобном для конечного приложения виде."""

    def __init__(self, host: str, api_key: str):
        """Высокоуровневый клиент. Предоставляет возможность работы с API в удобном для конечного приложения виде.

        :param host: хост API;
        :param api_key: ключ для доступа к API.
        """
        self.api_client = ExerciseAPIClient(host=host, api_key=api_key)

    def get_muscles(self, language: Literal["ru", "en"] = "ru") -> List[Dict[str, str]]:
        """Получение списка доступных мышц (мышечных групп).

        :param language: язык на котором требуется вывести список.
        :return: список объектов с оригинальным названием мышцы и переводом на требуемый язык.
        """
        response = self.api_client.get_muscles()
        if language == "en":
            muscles = [{"origin_name": muscle_name, "translate": muscle_name} for muscle_name in response.json()]
        else:
            lang_obj = Config.get_language_obj(language=language)
            muscles = [
                {"origin_name": muscle_name, "translate": lang_obj["muscles"].get(muscle_name, muscle_name)}
                for muscle_name in response.json()
            ]
        return muscles

    def search_exercise_by_primary_muscle(
        self,
        primary_muscle: str,
        language: Literal["ru", "en"] = "ru",
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Получение списка упражнений по указанной основной мышечной группе.

        :param primary_muscle: основная целевая мышечная группа;
        :param language: язык на котором требуется вывести список;
        :param limit: размер максимальной выдачи.
        :return: список объектов - упражнений на указанном языке.
        """
        response = self.api_client.search_exercise_by_primary_muscle(primary_muscle=primary_muscle)
        response_exercises = response.json() if len(response.json()) <= limit else response.json()[:limit]
        if language == "en":
            return response_exercises
        else:
            lang_obj = Config.get_language_obj(language=language)
            translated_exercises = []
            for exercise in response_exercises:
                exercise["Force"] = lang_obj["force_type"].get(exercise["Force"], exercise["Force"])
                exercise["Name"] = lang_obj["exercise_name"].get(exercise["Name"], exercise["Name"])
                for muscle_index, muscle in enumerate(exercise["Primary Muscles"]):
                    exercise["Primary Muscles"][muscle_index] = lang_obj["muscles"].get(muscle, muscle)
                for muscle_index, muscle in enumerate(exercise["SecondaryMuscles"]):
                    exercise["SecondaryMuscles"][muscle_index] = lang_obj["muscles"].get(muscle, muscle)
                exercise["Type"] = lang_obj["exercise_type"].get(exercise["Type"], exercise["Type"])
                for type_index, workout_type in enumerate(exercise["Workout Type"]):
                    exercise["Workout Type"][type_index] = lang_obj["workout_type"].get(workout_type, workout_type)
                translated_exercises.append(exercise)
            return translated_exercises

    def search_exercise_by_secondary_muscle(
        self,
        secondary_muscle: str,
        language: Literal["ru", "en"] = "ru",
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Получение списка упражнений по указанной основной мышечной группе.

        :param secondary_muscle: вспомогательная мышечная группа;
        :param language: язык на котором требуется вывести список;
        :param limit: размер максимальной выдачи.
        :return: список объектов - упражнений на указанном языке.
        """
        response = self.api_client.search_exercise_by_secondary_muscle(secondary_muscle=secondary_muscle)
        response_exercises = response.json() if len(response.json()) <= limit else response.json()[:limit]
        if language == "en":
            return response_exercises
        else:
            lang_obj = Config.get_language_obj(language=language)
            translated_exercises = []
            for exercise in response_exercises:
                exercise["Force"] = lang_obj["force_type"].get(exercise["Force"], exercise["Force"])
                exercise["Name"] = lang_obj["exercise_name"].get(exercise["Name"], exercise["Name"])
                for muscle_index, muscle in enumerate(exercise["Primary Muscles"]):
                    exercise["Primary Muscles"][muscle_index] = lang_obj["muscles"].get(muscle, muscle)
                for muscle_index, muscle in enumerate(exercise["SecondaryMuscles"]):
                    exercise["SecondaryMuscles"][muscle_index] = lang_obj["muscles"].get(muscle, muscle)
                exercise["Type"] = lang_obj["exercise_type"].get(exercise["Type"], exercise["Type"])
                for type_index, workout_type in enumerate(exercise["Workout Type"]):
                    exercise["Workout Type"][type_index] = lang_obj["workout_type"].get(workout_type, workout_type)
                translated_exercises.append(exercise)
            return translated_exercises

    def search_exercise_by_name(self, name: str, language: Literal["ru", "en"] = "ru") -> Dict[str, Any]:
        """Получение информации об упражнении по переданному названию.

        :param name: название упражнения;
        :param language: язык на котором требуется вывести список.
        :return: объект ответа сервиса.
        """
        lang_obj = Config.get_language_obj(language=language)
        response = self.api_client.search_exercise_by_name(name=name)
        exercise = response.json()[0]
        print()
        translated_exercise = {
            "Force": lang_obj["force_type"].get(exercise["Force"]) or exercise["Force"],
            "Name": lang_obj["exercise_name"].get(exercise["Name"]) or exercise["Name"],
            "Primary Muscles": [lang_obj["muscles"][muscle] for muscle in exercise["Primary Muscles"]],
            "SecondaryMuscles": [lang_obj["muscles"][muscle] for muscle in exercise["SecondaryMuscles"]],
            "Type": lang_obj["exercise_type"].get(exercise["Type"]) or exercise["Type"],
            "Workout Type": [lang_obj["workout_type"][workout_type] for workout_type in exercise["Workout Type"]],
            "Youtube link": exercise["Youtube link"]
        }
        return translated_exercise
