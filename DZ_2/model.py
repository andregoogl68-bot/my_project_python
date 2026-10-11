import ast                                                                   # Импортируем модуль для безопасного преобразования строки в объект Python
import os                                                                    # Импортируем модуль для работы с путями
from typing import Any, Optional                                             # Импортируем типы для аннотаций

from exceptions import (                                                     # Импортируем кастомные исключения
    BackupError,                                                             # Ошибка создания резервной копии
    ContactFileFormatError,                                                  # Ошибка формата файла
    ContactFileNotFoundError,                                                # Ошибка отсутствия файла
    ContactFileWriteError,                                                   # Ошибка записи файла
    ContactNotFoundError,                                                    # Ошибка поиска контакта
    DuplicatePhoneError,                                                     # Ошибка дубликата телефона
    EmptyFieldError,                                                         # Ошибка пустого поля
)

FILE_PATH: str = "contacts.txt"                                              # Путь к файлу контактов по умолчанию


class Contact:
    """Класс одного контакта телефонной книги."""

    def __init__(self, id: int, first: str, last: str, phone: str, comment: str = "") -> None:
        """
        Создаёт контакт.

        :param id: Уникальный идентификатор.
        :param first: Имя.
        :param last: Фамилия.
        :param phone: Номер телефона.
        :param comment: Комментарий (по умолчанию пустая строка).
        :return: None
        """
        self.id: int = id                                                    # Сохраняем ID
        self.first: str = first                                              # Сохраняем имя
        self.last: str = last                                                # Сохраняем фамилию
        self.phone: str = phone                                              # Сохраняем телефон
        self.comment: str = comment                                          # Сохраняем комментарий

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразует контакт в словарь для записи в файл.

        :return: Словарь с ключами 'Id', 'имя', 'фамилия', 'Номер', 'комментарий'.
        """
        return {                                                             # Возвращаем словарь для хранения
            "Id": self.id,                                                   # ID контакта
            "имя": self.first,                                               # Имя
            "фамилия": self.last,                                            # Фамилия
            "Номер": self.phone,                                             # Телефон
            "комментарий": self.comment,                                     # Комментарий
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Contact":
        """
        Создаёт контакт из словаря.

        :param data: Словарь с ключами 'Id', 'имя', 'фамилия', 'Номер', 'комментарий'.
        :return: Экземпляр Contact.
        """
        return cls(                                                          # Возвращаем новый контакт
            id=int(data.get("Id", 0)),                                       # ID приводим к целому числу
            first=data.get("имя", ""),                                       # Имя по умолчанию пустое
            last=data.get("фамилия", ""),                                    # Фамилия по умолчанию пустая
            phone=data.get("Номер", ""),                                     # Телефон по умолчанию пустой
            comment=data.get("комментарий", ""),                             # Комментарий по умолчанию пустой
        )

    def clone(self) -> "Contact":
        """
        Возвращает независимую копию контакта.

        :return: Новый экземпляр Contact с теми же значениями.
        """
        return Contact(self.id, self.first, self.last, self.phone, self.comment)  # Возвращаем копию

    def __eq__(self, other: object) -> bool:
        """
        Сравнивает два контакта по всем полям.

        :param other: Другой объект для сравнения.
        :return: True, если поля совпадают.
        """
        if not isinstance(other, Contact):                                   # Если сравниваем не с контактом
            return NotImplemented                                            # Возвращаем признак невозможности сравнения
        return (                                                             # Сравниваем все поля
            self.id == other.id                                              # Сравниваем ID
            and self.first == other.first                                    # Сравниваем имя
            and self.last == other.last                                      # Сравниваем фамилию
            and self.phone == other.phone                                    # Сравниваем телефон
            and self.comment == other.comment                                # Сравниваем комментарий
        )

    def __repr__(self) -> str:
        """
        Возвращает читаемое представление контакта.

        :return: Строка с полями контакта.
        """
        return (                                                             # Формируем строку представления
            f"Contact(id={self.id!r}, first={self.first!r}, "                # ID и имя
            f"last={self.last!r}, phone={self.phone!r}, "                    # Фамилия и телефон
            f"comment={self.comment!r})"                                     # Комментарий
        )


class ContactReader:
    """Класс чтения контактов из файла."""

    @staticmethod
    def load(path: str) -> list[Contact]:
        """
        Загружает список контактов из файла (строгий режим).

        :param path: Путь к файлу с контактами.
        :raises ContactFileNotFoundError: если файл не найден или недоступен.
        :raises ContactFileFormatError: если файл повреждён или имеет неверный формат.
        :return: Список экземпляров Contact.
        """
        if not os.path.exists(path):                                         # Проверяем существование файла
            raise ContactFileNotFoundError(f"Файл «{path}» не найден.")      # Возбуждаем кастомное исключение
        try:                                                                 # Пытаемся прочитать файл
            with open(path, "r", encoding="utf-8") as f:                     # Открываем файл на чтение
                content: str = f.read().strip()                              # Читаем содержимое и обрезаем пробелы
        except OSError as e:                                                 # Если возникла ошибка ввода-вывода
            raise ContactFileNotFoundError(f"Не удалось прочитать файл «{path}».") from e  # Пробрасываем кастомное
        if not content:                                                      # Если файл пуст
            return []                                                        # Возвращаем пустой список
        try:                                                                 # Пытаемся разобрать содержимое
            data: Any = ast.literal_eval(content)                            # Безопасно преобразуем в объект Python
        except (SyntaxError, ValueError) as e:                               # Если формат неверный
            raise ContactFileFormatError(f"Файл «{path}» повреждён или имеет неверный формат.") from e  # Возбуждаем
        if not isinstance(data, list):                                       # Проверяем, что это список
            raise ContactFileFormatError(f"Ожидался список контактов в файле «{path}».")  # Возбуждаем
        contacts: list[Contact] = []                                         # Создаём пустой список контактов
        for i, item in enumerate(data, start=1):                             # Перебираем элементы с нумерацией
            if not isinstance(item, dict):                                   # Проверяем, что элемент — словарь
                raise ContactFileFormatError(f"Элемент №{i} в файле «{path}» не является словарём.")  # Возбуждаем
            contacts.append(Contact.from_dict(item))                         # Добавляем контакт в список
        return contacts                                                      # Возвращаем список контактов

    @staticmethod
    def load_or_empty(path: str) -> list[Contact]:
        """
        Мягкая загрузка: при любой ошибке чтения возвращает пустой список.

        :param path: Путь к файлу с контактами.
        :return: Список экземпляров Contact или пустой список.
        """
        try:                                                                 # Пытаемся загрузить контакты
            return ContactReader.load(path)                                  # Возвращаем результат
        except (ContactFileNotFoundError, ContactFileFormatError):           # Если файла нет или он повреждён
            return []                                                        # Возвращаем пустой список


class ContactWriter:
    """Класс записи контактов в файл с созданием резервной копии .bak."""

    @staticmethod
    def save(contacts: list[Contact], path: str) -> None:
        """
        Сохраняет контакты в файл и делает резервную копию .bak.

        :param contacts: Список контактов для сохранения.
        :param path: Путь к файлу, в который сохраняются контакты.
        :raises BackupError: если не удалось создать резервную копию.
        :raises ContactFileWriteError: если не удалось записать файл.
        :return: None
        """
        if os.path.exists(path):                                             # Если файл уже существует
            try:                                                             # Пытаемся создать резервную копию
                with open(path, "r", encoding="utf-8") as src:               # Открываем существующий файл
                    backup: str = src.read()                                 # Читаем его содержимое
                with open(path + ".bak", "w", encoding="utf-8") as dst:      # Открываем .bak для записи
                    dst.write(backup)                                        # Записываем резервную копию
            except OSError as e:                                             # Если возникла ошибка ввода-вывода
                raise BackupError(f"Не удалось создать резервную копию «{path}.bak».") from e  # Возбуждаем
        try:                                                                 # Пытаемся записать основной файл
            with open(path, "w", encoding="utf-8") as f:                     # Открываем файл для перезаписи
                f.write("[\n")                                               # Начинаем список
                for c in contacts:                                           # Перебираем контакты
                    f.write(f"    {c.to_dict()!r},\n")                       # Записываем словарь в виде литерала Python
                f.write("]\n")                                               # Закрываем список
        except OSError as e:                                                 # Если возникла ошибка ввода-вывода
            raise ContactFileWriteError(f"Не удалось записать файл «{path}».") from e  # Возбуждаем


class PhoneBook:
    """Класс телефонного справочника: хранение и операции над контактами."""

    SEARCH_FIELDS: dict[str, str] = {                                        # Соответствие имён полей и атрибутов Contact
        "имя": "first",                                                      # Поле «имя» соответствует атрибуту first
        "фамилия": "last",                                                   # Поле «фамилия» соответствует атрибуту last
        "Номер": "phone",                                                    # Поле «Номер» соответствует атрибуту phone
        "комментарий": "comment",                                            # Поле «комментарий» соответствует атрибуту comment
    }

    def __init__(self, path: str = FILE_PATH) -> None:
        """
        Инициализирует телефонную книгу.

        Если файла нет или он повреждён — работа начинается с пустого справочника.

        :param path: Путь к файлу с контактами.
        :return: None
        """
        self.path: str = path                                                # Сохраняем путь к файлу
        self.contacts: list[Contact] = ContactReader.load_or_empty(path)     # Загружаем контакты в мягком режиме
        self.snapshot: list[Contact] = [c.clone() for c in self.contacts]    # Делаем снимок для отслеживания изменений

    @property
    def dirty(self) -> bool:
        """
        Признак наличия несохранённых изменений.

        :return: True, если текущее состояние отличается от снимка.
        """
        return self.contacts != self.snapshot                                # Сравниваем списки контактов со снимком

    def save(self) -> None:
        """
        Сохраняет текущее состояние книги на диск и обновляет снимок.

        :raises BackupError: если не удалось создать резервную копию.
        :raises ContactFileWriteError: если не удалось записать файл.
        :return: None
        """
        ContactWriter.save(self.contacts, self.path)                         # Сохраняем контакты через ContactWriter
        self.snapshot = [c.clone() for c in self.contacts]                   # Обновляем снимок

    def next_id(self) -> int:
        """
        Возвращает следующий свободный идентификатор контакта.

        :return: Максимальный существующий ID + 1, либо 1, если контактов нет.
        """
        return max((c.id for c in self.contacts), default=0) + 1             # Возвращаем максимальный ID + 1

    def get_by_id(self, cid: int) -> Contact:
        """
        Ищет контакт по идентификатору.

        :param cid: Идентификатор контакта.
        :raises ContactNotFoundError: если контакт не найден.
        :return: Экземпляр Contact.
        """
        for c in self.contacts:                                              # Перебираем контакты
            if c.id == cid:                                                  # Если ID совпал
                return c                                                     # Возвращаем контакт
        raise ContactNotFoundError(cid)                                      # Возбуждаем кастомное исключение

    def find_by_phone(self, phone: str) -> Optional[Contact]:
        """
        Ищет контакт по номеру телефона.

        :param phone: Номер телефона.
        :return: Экземпляр Contact или None, если не найден.
        """
        for c in self.contacts:                                              # Перебираем контакты
            if c.phone == phone:                                             # Если телефон совпал
                return c                                                     # Возвращаем контакт
        return None                                                          # Если не нашли — None

    def add(self, first: str, last: str, phone: str, comment: str = "") -> Contact:
        """
        Добавляет новый контакт в книгу.

        :param first: Имя контакта.
        :param last: Фамилия контакта.
        :param phone: Номер телефона.
        :param comment: Комментарий (по умолчанию пустая строка).
        :raises EmptyFieldError: если телефон пуст или пусты и имя, и фамилия.
        :raises DuplicatePhoneError: если телефон уже есть у другого контакта.
        :return: Добавленный контакт.
        """
        if not phone:                                                        # Проверяем обязательное поле телефона
            raise EmptyFieldError("телефон")                                 # Возбуждаем кастомное исключение
        if not first and not last:                                           # Проверяем, что указано хотя бы одно имя
            raise EmptyFieldError("имя или фамилия")                         # Возбуждаем кастомное исключение
        existing = self.find_by_phone(phone)                                 # Ищем контакт с таким телефоном
        if existing is not None:                                             # Если такой уже есть
            raise DuplicatePhoneError(phone, existing.id)                    # Возбуждаем кастомное исключение
        contact = Contact(self.next_id(), first, last, phone, comment)       # Создаём новый контакт
        self.contacts.append(contact)                                        # Добавляем контакт в список
        return contact                                                       # Возвращаем добавленный контакт

    def update(self, cid: int, first: str = "", last: str = "",
               phone: str = "", comment: str = "") -> Contact:
        """
        Обновляет поля существующего контакта (пустые значения игнорируются).

        :param cid: Идентификатор контакта.
        :param first: Новое имя (пустая строка — не менять).
        :param last: Новая фамилия (пустая строка — не менять).
        :param phone: Новый телефон (пустая строка — не менять).
        :param comment: Новый комментарий (пустая строка — не менять).
        :raises ContactNotFoundError: если контакт не найден.
        :raises DuplicatePhoneError: если новый телефон есть у другого контакта.
        :return: Обновлённый контакт.
        """
        c: Contact = self.get_by_id(cid)                                     # Находим контакт (может возбудить исключение)
        if phone:                                                            # Если телефон передан
            existing = self.find_by_phone(phone)                             # Ищем контакт с таким телефоном
            if existing is not None and existing.id != cid:                  # Если телефон занят другим контактом
                raise DuplicatePhoneError(phone, existing.id)                # Возбуждаем кастомное исключение
            c.phone = phone                                                  # Обновляем телефон
        if first:                                                            # Если имя передано
            c.first = first                                                  # Обновляем имя
        if last:                                                             # Если фамилия передана
            c.last = last                                                    # Обновляем фамилию
        if comment:                                                          # Если комментарий передан
            c.comment = comment                                              # Обновляем комментарий
        return c                                                             # Возвращаем обновлённый контакт

    def delete(self, cid: int) -> Contact:
        """
        Удаляет контакт по идентификатору.

        :param cid: Идентификатор контакта.
        :raises ContactNotFoundError: если контакт не найден.
        :return: Удалённый контакт.
        """
        c: Contact = self.get_by_id(cid)                                     # Находим контакт (может возбудить исключение)
        self.contacts.remove(c)                                              # Удаляем контакт из списка
        return c                                                             # Возвращаем удалённый контакт

    def search(self, query: str, field: Optional[str] = None) -> list[Contact]:
        """
        Ищет контакты по подстроке.

        :param query: Поисковый запрос (регистр не учитывается).
        :param field: Имя поля ('имя', 'фамилия', 'Номер', 'комментарий').
                      Если None — поиск по всем полям.
        :return: Список найденных контактов.
        """
        q: str = query.lower()                                               # Приводим запрос к нижнему регистру
        result: list[Contact] = []                                           # Создаём список результатов
        for c in self.contacts:                                              # Перебираем контакты
            if field:                                                        # Если указано конкретное поле
                attr = self.SEARCH_FIELDS.get(field, field)                  # Определяем атрибут Contact по имени поля
                if q in str(getattr(c, attr)).lower():                       # Ищем подстроку в значении атрибута
                    result.append(c)                                         # Добавляем контакт в результаты
            else:                                                            # Если поле не указано
                values = (c.id, c.first, c.last, c.phone, c.comment)         # Собираем все значения контакта
                if any(q in str(v).lower() for v in values):                 # Ищем подстроку среди значений
                    result.append(c)                                         # Добавляем контакт в результаты
        return result                                                        # Возвращаем список найденных контактов