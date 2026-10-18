"""
Кастомные исключения телефонного справочника.

Иерархия:
    PhoneBookError
    ├── StorageError
    │   ├── ContactFileNotFoundError
    │   ├── ContactFileFormatError
    │   ├── ContactFileWriteError
    │   └── BackupError
    ├── ValidationError
    │   ├── EmptyFieldError
    │   └── DuplicatePhoneError
    ├── ContactNotFoundError
    └── InvalidContactIDError
"""


class PhoneBookError(Exception):
    """Базовое исключение для всех ошибок телефонного справочника."""

    def __init__(self, message: str) -> None:
        super().__init__(message)                                    # Передаём сообщение в базовый Exception
        self.message: str = message                                  # Дублируем в атрибут для удобства


class StorageError(PhoneBookError):
    """Базовое исключение для ошибок файлового хранилища."""


class ContactFileNotFoundError(StorageError):
    """Файл с контактами не найден или недоступен для чтения."""


class ContactFileFormatError(StorageError):
    """Файл с контактами повреждён или имеет неверный формат."""


class ContactFileWriteError(StorageError):
    """Не удалось записать файл с контактами."""


class BackupError(StorageError):
    """Не удалось создать резервную копию .bak."""


class ValidationError(PhoneBookError):
    """Базовое исключение для ошибок валидации данных."""


class EmptyFieldError(ValidationError):
    """Обязательное поле пустое."""

    def __init__(self, field: str) -> None:
        super().__init__(f"Поле «{field}» не может быть пустым.")    # Формируем сообщение об ошибке
        self.field: str = field                                      # Сохраняем имя проблемного поля


class DuplicatePhoneError(ValidationError):
    """Телефон уже есть у другого контакта."""

    def __init__(self, phone: str, cid: int) -> None:
        super().__init__(f"Телефон {phone} уже есть у контакта ID={cid}.")  # Формируем сообщение
        self.phone: str = phone                                      # Сохраняем телефон
        self.cid: int = cid                                          # Сохраняем ID конфликтующего контакта


class ContactNotFoundError(PhoneBookError):
    """Контакт с указанным ID не найден."""

    def __init__(self, cid: int) -> None:
        super().__init__(f"Контакт с ID={cid} не найден.")           # Формируем сообщение
        self.cid: int = cid                                          # Сохраняем ID


class InvalidContactIDError(PhoneBookError):
    """Введённое значение ID не является целым числом."""

    def __init__(self, raw: str) -> None:
        super().__init__(f"ID «{raw}» не является целым числом.")    # Формируем сообщение
        self.raw: str = raw                                          # Сохраняем исходный ввод