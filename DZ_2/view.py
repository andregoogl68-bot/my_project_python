from typing import Optional                                                  # Импортируем тип Optional для аннотаций

from exceptions import InvalidContactIDError                                 # Импортируем кастомное исключение для ID
from model import Contact                                                    # Импортируем класс контакта из модели


def show_contacts(contacts: list[Contact]) -> None:
    """
    Выводит список контактов в виде таблицы.

    :param contacts: Список контактов для отображения.
    :return: None
    """
    if not contacts:                                                         # Если список пуст
        print("Контактов нет.")                                              # Сообщаем пользователю
        return                                                               # Выходим из функции
    print(f"\n{'ID':<4} {'Имя':<12} {'Фамилия':<14} {'Телефон':<20} Комментарий")  # Печатаем заголовок
    print("-" * 80)                                                          # Печатаем разделитель
    for c in contacts:                                                       # Перебираем контакты
        print(f"{c.id:<4} {c.first:<12} {c.last:<14} {c.phone:<20} {c.comment}")  # Печатаем строку контакта


def show_message(message: str) -> None:
    """
    Выводит информационное сообщение пользователю.

    :param message: Текст сообщения.
    :return: None
    """
    print(message)                                                           # Печатаем сообщение


def show_error(error: Exception) -> None:
    """
    Выводит сообщение об ошибке в едином формате.

    :param error: Исключение (обычно кастомное из exceptions.py).
    :return: None
    """
    print(f"[Ошибка] {error}")                                               # Печатаем текст ошибки с пометкой


def show_main_menu() -> None:
    """
    Печатает главное меню.

    :return: None
    """
    print(                                                                   # Печатаем меню одной конструкцией
        "\n=== Телефонный справочник ===\n"                                  # Заголовок меню
        "1. Показать контакты\n"                                             # Пункт 1
        "2. Добавить\n"                                                      # Пункт 2
        "3. Редактировать\n"                                                 # Пункт 3
        "4. Удалить\n"                                                       # Пункт 4
        "5. Поиск\n"                                                         # Пункт 5
        "6. Сохранить\n"                                                     # Пункт 6
        "7. Загрузить из файла\n"                                            # Пункт 7
        "0. Выход"                                                           # Пункт 0
    )


def show_search_menu() -> None:
    """
    Печатает меню поиска.

    :return: None
    """
    print("\n1-имя  2-фамилия  3-телефон  4-комментарий  5-общий поиск")     # Печатаем варианты поиска


def ask(prompt: str) -> str:
    """
    Запрашивает у пользователя строку.

    :param prompt: Приглашение к вводу.
    :return: Введённая строка без пробелов по краям.
    """
    return input(prompt).strip()                                             # Читаем строку и убираем пробелы по краям


def ask_int(prompt: str) -> int:
    """
    Запрашивает у пользователя целое число.

    :param prompt: Приглашение к вводу.
    :raises InvalidContactIDError: если ввод не является целым числом.
    :return: Целое число.
    """
    raw: str = input(prompt).strip()                                         # Читаем строку и убираем пробелы
    try:                                                                     # Пытаемся преобразовать в int
        return int(raw)                                                      # Возвращаем целое число
    except ValueError as e:                                                  # Если ввод не число
        raise InvalidContactIDError(raw) from e                              # Возбуждаем кастомное исключение


def confirm_save() -> bool:
    """
    Спрашивает пользователя, сохранять ли изменения.

    :return: True, если пользователь ответил положительно.
    """
    answer = input("Есть несохранённые изменения. Сохранить? (y/n): ").strip().lower()  # Читаем ответ
    return answer in ("y", "yes", "д", "да")                                 # Возвращаем True для положительных ответов