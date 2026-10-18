"""
Тесты телефонного справочника (unittest + pytest).

Запуск:
    python test_directory.py                  # только unittest
    python -m pytest test_directory.py -v     # unittest + pytest

Все тесты изолированы: каждый работает в собственной временной
директории, реальный файл ``contacts.txt`` не затрагивается.
"""

import ast                                                                   # Для проверки содержимого файла
import io                                                                    # Для перехвата stdout
import os                                                                    # Для работы с путями
import tempfile                                                              # Для временных директорий
import unittest                                                              # Базовый фреймворк
from contextlib import redirect_stdout                                       # Для перехвата вывода
from unittest.mock import patch                                              # Для подмены input/open

import pytest                                                                # Фреймворк pytest

from exceptions import (                                                     # Кастомные исключения
    BackupError,                                                             # Ошибка резервной копии
    ContactFileFormatError,                                                  # Ошибка формата файла
    ContactFileNotFoundError,                                                # Ошибка отсутствия файла
    ContactFileWriteError,                                                   # Ошибка записи файла
    ContactNotFoundError,                                                    # Контакт не найден
    DuplicatePhoneError,                                                     # Дубликат телефона
    EmptyFieldError,                                                         # Пустое поле
    InvalidContactIDError,                                                   # Некорректный ID
    PhoneBookError,                                                          # Базовое исключение
    StorageError,                                                            # Базовое хранилище
    ValidationError,                                                         # Базовая валидация
)                                                                            # Конец импорта исключений
from model import Contact, ContactReader, ContactWriter, PhoneBook           # Тестируемые классы


# =============================================================================
# UNITTEST — модель, контакт
# =============================================================================

class TestContact(unittest.TestCase):                                        # Класс тестов Contact
    """Тесты класса Contact."""                                              # Докстрока класса

    def test_to_dict(self):                                                  # Тест метода to_dict
        """to_dict возвращает словарь с правильными ключами."""             # Докстрока теста
        c = Contact(1, "Иван", "Иванов", "+79990001122", "друг")             # Создаём контакт
        self.assertEqual(                                                    # Проверяем равенство
            c.to_dict(),                                                     # Результат to_dict()
            {                                                                # Ожидаемый словарь
                "Id": 1,                                                     # Ожидаемый Id
                "имя": "Иван",                                               # Ожидаемое имя
                "фамилия": "Иванов",                                         # Ожидаемая фамилия
                "Номер": "+79990001122",                                     # Ожидаемый телефон
                "комментарий": "друг",                                       # Ожидаемый комментарий
            },                                                               # Конец словаря
        )                                                                    # Конец assertEqual

    def test_from_dict_ok(self):                                             # Тест from_dict с корректными данными
        """from_dict корректно создаёт контакт."""                           # Докстрока
        data = {                                                             # Готовим словарь
            "Id": 5, "имя": "Пётр", "фамилия": "Петров",                     # Id, имя, фамилия
            "Номер": "+79993334455", "комментарий": "",                      # Телефон и комментарий
        }                                                                    # Конец словаря
        c = Contact.from_dict(data)                                          # Создаём контакт из словаря
        self.assertEqual(c.id, 5)                                            # Проверяем Id
        self.assertEqual(c.first, "Пётр")                                    # Проверяем имя
        self.assertEqual(c.last, "Петров")                                   # Проверяем фамилию
        self.assertEqual(c.phone, "+79993334455")                            # Проверяем телефон
        self.assertEqual(c.comment, "")                                      # Проверяем комментарий

    def test_from_dict_defaults(self):                                       # Тест значений по умолчанию
        """Отсутствующие поля получают значения по умолчанию."""             # Докстрока
        c = Contact.from_dict({})                                            # Пустой словарь
        self.assertEqual(c.id, 0)                                            # Id по умолчанию 0
        self.assertEqual(c.first, "")                                        # Имя по умолчанию ""
        self.assertEqual(c.last, "")                                         # Фамилия по умолчанию ""
        self.assertEqual(c.phone, "")                                        # Телефон по умолчанию ""
        self.assertEqual(c.comment, "")                                      # Комментарий по умолчанию ""

    def test_from_dict_various_ids(self):                                    # Тест разных вариантов Id
        """subTest: from_dict корректно разбирает разные варианты Id."""     # Докстрока
        for raw, expected in [(1, 1), ("2", 2), (10, 10), (0, 0)]:           # Перебираем пары
            with self.subTest(raw=raw):                                      # subTest для каждого варианта
                c = Contact.from_dict({                                      # Создаём контакт
                    "Id": raw, "имя": "", "фамилия": "", "Номер": "", "комментарий": "",  # Данные
                })                                                           # Конец словаря
                self.assertEqual(c.id, expected)                             # Проверяем Id

    def test_from_dict_bad_id_string(self):                                  # Тест нецелого Id (строка)
        """Нецелый Id превращается в ContactFileFormatError."""             # Докстрока
        with self.assertRaisesRegex(ContactFileFormatError, "не является целым числом"):  # Ожидаем исключение
            Contact.from_dict({                                              # Пытаемся создать
                "Id": "abc", "имя": "X", "фамилия": "Y",                     # Id строка
                "Номер": "", "комментарий": "",                              # Остальное пусто
            })                                                               # Конец вызова

    def test_from_dict_bad_id_type(self):                                    # Тест некорректного типа Id
        """Некорректный тип Id (список) тоже даёт ContactFileFormatError."""  # Докстрока
        with self.assertRaises(ContactFileFormatError):                      # Ожидаем исключение
            Contact.from_dict({                                              # Пытаемся создать
                "Id": [1, 2, 3], "имя": "X", "фамилия": "Y",                 # Id — список
                "Номер": "", "комментарий": "",                              # Остальное пусто
            })                                                               # Конец вызова

    def test_equality(self):                                                 # Тест равенства контактов
        """Два контакта с одинаковыми полями равны."""                       # Докстрока
        c1 = Contact(1, "A", "B", "+1")                                      # Первый контакт
        c2 = Contact(1, "A", "B", "+1")                                      # Второй контакт — копия
        c3 = Contact(2, "A", "B", "+1")                                      # Третий контакт — другой Id
        self.assertEqual(c1, c2)                                             # c1 == c2
        self.assertNotEqual(c1, c3)                                          # c1 != c3

    def test_equality_with_other_type(self):                                 # Тест сравнения с другим типом
        """Сравнение с объектом другого типа — не равны."""                  # Докстрока
        self.assertNotEqual(Contact(1, "A", "B", "+1"), "not a contact")     # Контакт не равен строке

    def test_clone_independent(self):                                        # Тест независимости клона
        """clone возвращает независимую копию."""                            # Докстрока
        c = Contact(1, "A", "B", "+1", "x")                                  # Исходный контакт
        c2 = c.clone()                                                       # Клон
        self.assertEqual(c, c2)                                              # Клон равен исходному
        self.assertIsNot(c, c2)                                              # Но это разные объекты
        c2.first = "Z"                                                       # Меняем поле клона
        self.assertNotEqual(c, c2)                                           # Теперь контакты не равны


# =============================================================================
# UNITTEST — чтение из файла
# =============================================================================

class TestContactReader(unittest.TestCase):                                  # Класс тестов ContactReader
    """Тесты ContactReader."""                                               # Докстрока класса

    def setUp(self):                                                         # Подготовка перед каждым тестом
        """Создаём временную директорию под каждый тест."""                  # Докстрока
        self._tmp = tempfile.TemporaryDirectory()                            # Создаём временную директорию
        self.tmpdir = self._tmp.name                                         # Запоминаем путь
        self.path = os.path.join(self.tmpdir, "contacts.txt")                # Путь к файлу контактов

    def tearDown(self):                                                      # Уборка после каждого теста
        """Удаляем временную директорию после теста."""                      # Докстрока
        self._tmp.cleanup()                                                  # Удаляем директорию

    def test_load_missing_file(self):                                        # Тест отсутствующего файла
        """Отсутствующий файл — ContactFileNotFoundError."""                 # Докстрока
        with self.assertRaises(ContactFileNotFoundError):                    # Ожидаем исключение
            ContactReader.load(self.path)                                    # Пытаемся загрузить

    def test_load_empty_file(self):                                          # Тест пустого файла
        """Пустой файл даёт пустой список."""                                # Докстрока
        with open(self.path, "w", encoding="utf-8"):                         # Создаём пустой файл
            pass                                                             # Ничего не пишем
        self.assertEqual(ContactReader.load(self.path), [])                  # Результат — пустой список

    def test_load_valid(self):                                               # Тест корректного файла
        """Корректный файл успешно читается."""                              # Докстрока
        with open(self.path, "w", encoding="utf-8") as f:                    # Открываем файл на запись
            f.write("[{'Id': 1, 'имя': 'A', 'фамилия': 'B', "                # Первая часть литерала
                    "'Номер': '+1', 'комментарий': ''}]")                    # Вторая часть литерала
        contacts = ContactReader.load(self.path)                             # Загружаем контакты
        self.assertEqual(len(contacts), 1)                                   # Проверяем количество
        self.assertEqual(contacts[0].id, 1)                                  # Проверяем Id
        self.assertEqual(contacts[0].first, "A")                             # Проверяем имя

    def test_load_bad_syntax(self):                                          # Тест сломанного синтаксиса
        """Повреждённый синтаксис — ContactFileFormatError."""               # Докстрока
        with open(self.path, "w", encoding="utf-8") as f:                    # Открываем файл на запись
            f.write("[{'Id': 1, BROKEN")                                     # Пишем некорректный литерал
        with self.assertRaises(ContactFileFormatError):                      # Ожидаем исключение
            ContactReader.load(self.path)                                    # Пытаемся загрузить

    def test_load_not_list(self):                                            # Тест «не список» в файле
        """Не список в файле — ContactFileFormatError."""                    # Докстрока
        with open(self.path, "w", encoding="utf-8") as f:                    # Открываем файл на запись
            f.write("42")                                                    # Пишем число, а не список
        with self.assertRaisesRegex(ContactFileFormatError, "Ожидался список"):  # Ожидаем исключение
            ContactReader.load(self.path)                                    # Пытаемся загрузить

    def test_load_non_dict_item(self):                                       # Тест элемента не-словаря
        """Элемент списка не словарь — ContactFileFormatError."""            # Докстрока
        with open(self.path, "w", encoding="utf-8") as f:                    # Открываем файл на запись
            f.write("[1, 2, 3]")                                             # Пишем числа вместо словарей
        with self.assertRaisesRegex(ContactFileFormatError, "не является словарём"):  # Ожидаем исключение
            ContactReader.load(self.path)                                    # Пытаемся загрузить

    def test_load_or_empty_missing(self):                                    # Тест мягкой загрузки отсутствующего
        """Мягкая загрузка отсутствующего файла — []."""                     # Докстрока
        self.assertEqual(ContactReader.load_or_empty(self.path), [])         # Результат — пустой список

    def test_load_or_empty_broken(self):                                     # Тест мягкой загрузки битого
        """Мягкая загрузка повреждённого файла — []."""                      # Докстрока
        with open(self.path, "w", encoding="utf-8") as f:                    # Открываем файл на запись
            f.write("BROKEN")                                                # Пишем мусор
        self.assertEqual(ContactReader.load_or_empty(self.path), [])         # Результат — пустой список


# =============================================================================
# UNITTEST — запись в файл
# =============================================================================

class TestContactWriter(unittest.TestCase):                                  # Класс тестов ContactWriter
    """Тесты ContactWriter."""                                               # Докстрока класса

    def setUp(self):                                                         # Подготовка перед каждым тестом
        self._tmp = tempfile.TemporaryDirectory()                            # Создаём временную директорию
        self.tmpdir = self._tmp.name                                         # Запоминаем путь
        self.path = os.path.join(self.tmpdir, "out.txt")                     # Путь к файлу вывода

    def tearDown(self):                                                      # Уборка после теста
        self._tmp.cleanup()                                                  # Удаляем директорию

    def test_save_empty_list(self):                                          # Тест сохранения пустого списка
        """Сохранение пустого списка даёт валидный пустой файл."""           # Докстрока
        ContactWriter.save([], self.path)                                    # Сохраняем пустой список
        self.assertTrue(os.path.exists(self.path))                           # Файл создан
        with open(self.path, encoding="utf-8") as f:                         # Открываем файл
            self.assertEqual(ast.literal_eval(f.read()), [])                 # Внутри валидный []

    def test_save_one_contact(self):                                         # Тест сохранения одного контакта
        """Сохранение одного контакта читается обратно."""                   # Докстрока
        ContactWriter.save([Contact(1, "A", "B", "+1", "x")], self.path)     # Сохраняем контакт
        with open(self.path, encoding="utf-8") as f:                         # Открываем файл
            content = f.read()                                               # Читаем содержимое
        self.assertIn("'Id': 1", content)                                    # Id присутствует
        self.assertIn("'имя': 'A'", content)                                 # Имя присутствует

    def test_save_creates_backup(self):                                      # Тест создания резервной копии
        """Повторное сохранение создаёт .bak."""                             # Докстрока
        ContactWriter.save([Contact(1, "A", "B", "+1")], self.path)          # Первое сохранение
        ContactWriter.save([Contact(2, "C", "D", "+2")], self.path)          # Второе сохранение
        self.assertTrue(os.path.exists(self.path + ".bak"))                  # .bak создан


# =============================================================================
# UNITTEST — основная логика PhoneBook
# =============================================================================

class TestPhoneBook(unittest.TestCase):                                      # Класс тестов PhoneBook
    """Тесты PhoneBook: добавление, поиск, обновление, удаление, файлы."""   # Докстрока класса

    def setUp(self):                                                         # Подготовка перед тестом
        """Свежая временная директория и пустая книга под каждый тест."""    # Докстрока
        self._tmp = tempfile.TemporaryDirectory()                            # Временная директория
        self.tmpdir = self._tmp.name                                         # Путь к ней
        self.path = os.path.join(self.tmpdir, "contacts.txt")                # Путь к файлу
        self.book = PhoneBook(self.path)                                     # Новая пустая книга

    def tearDown(self):                                                      # Уборка после теста
        """Удаляем временную директорию после теста."""                      # Докстрока
        self._tmp.cleanup()                                                  # Удаляем директорию

    # ---------- Добавление ----------

    def test_add_contact(self):                                              # Тест добавления контакта
        """Добавление контакта возвращает его и увеличивает список."""       # Докстрока
        c = self.book.add("Иван", "Иванов", "+79990001122", "друг")          # Добавляем
        self.assertEqual(c.id, 1)                                            # Id == 1
        self.assertEqual(len(self.book.contacts), 1)                         # Длина списка == 1
        self.assertTrue(self.book.dirty)                                     # Есть несохранённые изменения

    def test_add_empty_phone(self):                                          # Тест пустого телефона
        """Пустой телефон — EmptyFieldError."""                              # Докстрока
        with self.assertRaisesRegex(EmptyFieldError, "телефон"):             # Ожидаем ошибку
            self.book.add("A", "B", "")                                      # Пытаемся добавить

    def test_add_empty_name_and_last(self):                                  # Тест отсутствия имени и фамилии
        """Нет ни имени, ни фамилии — EmptyFieldError."""                    # Докстрока
        with self.assertRaisesRegex(EmptyFieldError, "имя или фамилия"):     # Ожидаем ошибку
            self.book.add("", "", "+1")                                      # Пытаемся добавить

    def test_add_duplicate_phone(self):                                      # Тест дубликата телефона
        """Дубликат телефона — DuplicatePhoneError."""                       # Докстрока
        self.book.add("A", "B", "+1")                                        # Первый контакт
        with self.assertRaises(DuplicatePhoneError):                         # Ожидаем ошибку
            self.book.add("C", "D", "+1")                                    # Пытаемся добавить дубликат

    # ---------- Поиск по ID ----------

    def test_get_by_id_ok(self):                                             # Тест поиска по Id
        """get_by_id находит контакт."""                                     # Докстрока
        c = self.book.add("A", "B", "+1")                                    # Добавляем контакт
        self.assertIs(self.book.get_by_id(c.id), c)                          # Тот же объект возвращён

    def test_get_by_id_not_found(self):                                      # Тест поиска несуществующего Id
        """Несуществующий ID — ContactNotFoundError."""                      # Докстрока
        with self.assertRaises(ContactNotFoundError):                        # Ожидаем ошибку
            self.book.get_by_id(999)                                         # Пытаемся найти

    # ---------- Поиск по полям ----------

    def test_search_by_name(self):                                           # Тест поиска по имени
        """Поиск по имени находит один контакт."""                           # Докстрока
        self.book.add("Иван", "Иванов", "+1")                                # Первый контакт
        self.book.add("Пётр", "Петров", "+2")                                # Второй контакт
        results = self.book.search("иван", "имя")                            # Ищем по имени
        self.assertEqual(len(results), 1)                                    # Ровно один результат
        self.assertEqual(results[0].first, "Иван")                           # Нашли Ивана

    def test_search_by_phone(self):                                          # Тест поиска по телефону
        """Поиск по телефону находит один контакт."""                        # Докстрока
        self.book.add("A", "B", "+79990001122")                              # Первый контакт
        self.book.add("C", "D", "+79993334455")                              # Второй контакт
        results = self.book.search("0001", "Номер")                          # Ищем по номеру
        self.assertEqual(len(results), 1)                                    # Ровно один результат
        self.assertEqual(results[0].phone, "+79990001122")                   # Совпал нужный телефон

    def test_search_general(self):                                           # Тест общего поиска
        """Общий поиск ищет по всем полям."""                                # Докстрока
        self.book.add("Иван", "Иванов", "+1", "друг")                        # Первый контакт
        self.book.add("Пётр", "Петров", "+2", "коллега")                     # Второй контакт
        results = self.book.search("друг")                                   # Ищем без указания поля
        self.assertEqual(len(results), 1)                                    # Ровно один результат
        self.assertEqual(results[0].first, "Иван")                           # Нашли Ивана

    def test_search_by_all_fields(self):                                     # Тест поиска по каждому полю
        """subTest: поиск работает по каждому полю."""                       # Докстрока
        self.book.add("Иван", "Иванов", "+79990001122", "друг")              # Добавляем контакт
        for field, query in [                                                # Перебираем пары
            ("имя", "Иван"),                                                 # Поиск по имени
            ("фамилия", "Иванов"),                                           # Поиск по фамилии
            ("Номер", "+7999000"),                                           # Поиск по телефону
            ("комментарий", "друг"),                                         # Поиск по комментарию
        ]:                                                                   # Конец списка
            with self.subTest(field=field):                                  # subTest для каждого поля
                self.assertEqual(len(self.book.search(query, field)), 1)     # Ровно один результат

    def test_search_case_insensitive(self):                                  # Тест регистронезависимости
        """Поиск не зависит от регистра."""                                  # Докстрока
        self.book.add("ИВАН", "ИВАНОВ", "+1")                                # Контакт заглавными
        self.assertEqual(len(self.book.search("иван")), 1)                   # Ищем строчными — находим

    def test_search_no_results(self):                                        # Тест поиска без результатов
        """Заведомо несуществующий запрос — пустой список."""                # Докстрока
        self.book.add("A", "B", "+1")                                        # Добавляем контакт
        self.assertEqual(self.book.search("zzz"), [])                        # Результатов нет

    # ---------- Обновление ----------

    def test_update_contact(self):                                           # Тест обновления контакта
        """Обновление меняет все переданные поля."""                         # Докстрока
        c = self.book.add("A", "B", "+1")                                    # Добавляем контакт
        updated = self.book.update(c.id, first="Новое", last="Фам",          # Обновляем поля
                                   phone="+2", comment="c")                  # Продолжение вызова
        self.assertEqual(updated.first, "Новое")                             # Имя обновилось
        self.assertEqual(updated.last, "Фам")                                # Фамилия обновилась
        self.assertEqual(updated.phone, "+2")                                # Телефон обновился
        self.assertEqual(updated.comment, "c")                               # Комментарий обновился

    def test_update_ignores_empty(self):                                     # Тест игнорирования пустых полей
        """Пустые значения не меняют поля."""                                # Докстрока
        c = self.book.add("A", "B", "+1", "x")                               # Добавляем контакт
        self.book.update(c.id, first="", last="", phone="", comment="")      # Обновляем пустыми
        self.assertEqual(c.first, "A")                                       # Имя не изменилось
        self.assertEqual(c.comment, "x")                                     # Комментарий не изменился

    def test_update_duplicate_phone(self):                                   # Тест дубликата телефона при update
        """Смена телефона на занятый — DuplicatePhoneError."""               # Докстрока
        c1 = self.book.add("A", "B", "+1")                                   # Первый контакт
        self.book.add("C", "D", "+2")                                        # Второй контакт
        with self.assertRaises(DuplicatePhoneError):                         # Ожидаем ошибку
            self.book.update(c1.id, phone="+2")                              # Пытаемся поставить занятый

    def test_update_same_phone_ok(self):                                     # Тест смены на тот же телефон
        """Смена телефона на тот же — не ошибка."""                          # Докстрока
        c = self.book.add("A", "B", "+1")                                    # Добавляем контакт
        self.book.update(c.id, phone="+1")                                   # Ставим тот же телефон
        self.assertEqual(c.phone, "+1")                                      # Телефон не изменился

    def test_update_not_found(self):                                         # Тест update несуществующего
        """Несуществующий ID при обновлении — ContactNotFoundError."""       # Докстрока
        with self.assertRaises(ContactNotFoundError):                        # Ожидаем ошибку
            self.book.update(999, first="A")                                 # Пытаемся обновить

    # ---------- Удаление ----------

    def test_delete_contact(self):                                           # Тест удаления контакта
        """Удаление убирает контакт и возвращает его."""                     # Докстрока
        c = self.book.add("A", "B", "+1")                                    # Добавляем контакт
        deleted = self.book.delete(c.id)                                     # Удаляем
        self.assertEqual(deleted.id, c.id)                                   # Вернулся тот же Id
        self.assertEqual(len(self.book.contacts), 0)                         # Список пуст

    def test_delete_not_found(self):                                         # Тест удаления несуществующего
        """Удаление несуществующего ID — ContactNotFoundError."""            # Докстрока
        with self.assertRaises(ContactNotFoundError):                        # Ожидаем ошибку
            self.book.delete(999)                                            # Пытаемся удалить

    # ---------- Работа с файлом ----------

    def test_save_and_load_roundtrip(self):                                  # Тест roundtrip save/load
        """save + новая PhoneBook = те же данные."""                         # Докстрока
        self.book.add("Иван", "Иванов", "+1", "x")                           # Добавляем контакт
        self.book.save()                                                     # Сохраняем
        self.assertFalse(self.book.dirty)                                    # Флаг dirty сброшен

        book2 = PhoneBook(self.path)                                         # Новая книга из файла
        self.assertEqual(len(book2.contacts), 1)                             # Один контакт
        self.assertEqual(book2.contacts[0].first, "Иван")                    # Имя совпало
        self.assertEqual(book2.contacts[0].comment, "x")                     # Комментарий совпал

    def test_save_creates_backup(self):                                      # Тест создания резервной копии
        """Повторное сохранение создаёт .bak."""                             # Докстрока
        self.book.add("A", "B", "+1")                                        # Первый контакт
        self.book.save()                                                     # Первое сохранение
        self.book.add("C", "D", "+2")                                        # Второй контакт
        self.book.save()                                                     # Второе сохранение
        self.assertTrue(os.path.exists(self.path + ".bak"))                  # .bak создан

    def test_next_id(self):                                                  # Тест next_id
        """next_id растёт по мере добавления."""                             # Докстрока
        self.assertEqual(self.book.next_id(), 1)                             # Изначально 1
        self.book.add("A", "B", "+1")                                        # Добавляем контакт
        self.assertEqual(self.book.next_id(), 2)                             # Теперь 2

    def test_load_from_dirty_state(self):                                    # Тест строгой загрузки из файла
        """Загрузка через ContactReader.load сохраняет данные."""            # Докстрока
        self.book.add("A", "B", "+1")                                        # Добавляем контакт
        self.book.save()                                                     # Сохраняем
        contacts = ContactReader.load(self.path)                             # Загружаем строго
        self.assertEqual(len(contacts), 1)                                   # Один контакт
        self.assertEqual(contacts[0].first, "A")                             # Имя совпало

    # ---------- Граничные условия ----------

    def test_add_empty_contact_subtest(self):                                # subTest: разные пустые комбинации
        """subTest: пустые обязательные поля → EmptyFieldError."""           # Докстрока
        cases = [                                                            # Список вариантов
            ("", "", ""),       # всё пусто                                   # Всё пусто
            ("", "", "+1"),     # нет имени и фамилии                        # Нет имени и фамилии
            ("A", "", ""),      # нет телефона                               # Нет телефона
            ("", "B", ""),      # нет телефона                               # Нет телефона
        ]                                                                    # Конец списка
        for first, last, phone in cases:                                     # Перебираем варианты
            with self.subTest(first=first, last=last, phone=phone):          # subTest для каждого
                with self.assertRaises(EmptyFieldError):                     # Ожидаем ошибку
                    self.book.add(first, last, phone)                        # Пытаемся добавить

    def test_add_only_first_name(self):                                      # Тест только имени
        """Только имя, фамилия пустая — разрешено."""                        # Докстрока
        c = self.book.add("Иван", "", "+1")                                  # Добавляем только имя
        self.assertEqual(c.first, "Иван")                                    # Имя сохранено
        self.assertEqual(c.last, "")                                         # Фамилия пустая

    def test_add_only_last_name(self):                                       # Тест только фамилии
        """Только фамилия, имя пустое — разрешено."""                        # Докстрока
        c = self.book.add("", "Иванов", "+1")                                # Добавляем только фамилию
        self.assertEqual(c.first, "")                                        # Имя пустое
        self.assertEqual(c.last, "Иванов")                                   # Фамилия сохранена

    def test_next_id_after_delete_last(self):                                # Тест next_id после удаления
        """next_id после удаления последнего уменьшается (текущее поведение)."""  # Докстрока
        self.book.add("A", "B", "+1")                                        # Первый контакт
        c2 = self.book.add("C", "D", "+2")                                   # Второй контакт
        self.assertEqual(self.book.next_id(), 3)                             # Максимальный + 1
        self.book.delete(c2.id)                                              # Удаляем последний
        self.assertEqual(self.book.next_id(), 2)                             # Теперь снова 2


# =============================================================================
# UNITTEST — представление view
# =============================================================================

class TestView(unittest.TestCase):                                           # Класс тестов view
    """Тесты view (input и print замоканы)."""                               # Докстрока класса

    def test_ask_int_ok(self):                                               # Тест корректного ввода
        import view                                                          # Импорт view
        with patch("builtins.input", return_value="42"):                     # Подменяем input
            self.assertEqual(view.ask_int("> "), 42)                         # Результат — 42

    def test_ask_int_bad(self):                                              # Тест некорректного ввода
        import view                                                          # Импорт view
        with patch("builtins.input", return_value="abc"):                    # Подменяем input
            with self.assertRaisesRegex(InvalidContactIDError, "не является целым числом"):  # Ожидаем ошибку
                view.ask_int("> ")                                           # Пытаемся разобрать

    def test_ask_strips(self):                                               # Тест обрезки пробелов
        import view                                                          # Импорт view
        with patch("builtins.input", return_value="  hello  "):              # Ввод с пробелами
            self.assertEqual(view.ask("> "), "hello")                        # Пробелы убраны

    def test_confirm_save_yes(self):                                         # Тест положительного ответа
        import view                                                          # Импорт view
        for answer in ("y", "yes", "д", "да"):                               # Перебираем ответы
            with self.subTest(answer=answer):                                # subTest для каждого
                with patch("builtins.input", return_value=answer):           # Подменяем input
                    self.assertTrue(view.confirm_save())                     # Возвращается True

    def test_confirm_save_no(self):                                          # Тест отрицательного ответа
        import view                                                          # Импорт view
        with patch("builtins.input", return_value="n"):                      # Подменяем input
            self.assertFalse(view.confirm_save())                            # Возвращается False

    def test_show_contacts_empty(self):                                      # Тест пустого списка
        import view                                                          # Импорт view
        buf = io.StringIO()                                                  # Буфер вывода
        with redirect_stdout(buf):                                           # Перехватываем stdout
            view.show_contacts([])                                           # Вызываем функцию
        self.assertIn("Контактов нет", buf.getvalue())                       # Есть сообщение

    def test_show_contacts_table(self):                                      # Тест таблицы
        import view                                                          # Импорт view
        buf = io.StringIO()                                                  # Буфер вывода
        with redirect_stdout(buf):                                           # Перехватываем stdout
            view.show_contacts([Contact(1, "A", "B", "+1")])                 # Печатаем таблицу
        out = buf.getvalue()                                                 # Получаем вывод
        self.assertIn("ID", out)                                             # Есть заголовок
        self.assertIn("A", out)                                              # Есть имя

    def test_show_error(self):                                               # Тест вывода ошибки
        import view                                                          # Импорт view
        buf = io.StringIO()                                                  # Буфер вывода
        with redirect_stdout(buf):                                           # Перехватываем stdout
            view.show_error(PhoneBookError("тест"))                          # Печатаем ошибку
        self.assertIn("[Ошибка]", buf.getvalue())                            # Есть пометка
        self.assertIn("тест", buf.getvalue())                                # Есть текст


# =============================================================================
# UNITTEST — иерархия исключений
# =============================================================================

class TestExceptionHierarchy(unittest.TestCase):                             # Класс тестов иерархии
    """Наследование кастомных исключений от PhoneBookError."""               # Докстрока класса

    def test_storage_errors(self):                                           # Тест ошибок хранилища
        """Все ошибки хранилища — потомки StorageError и PhoneBookError."""  # Докстрока
        for exc in (ContactFileNotFoundError, ContactFileFormatError,        # Перебираем классы
                    ContactFileWriteError, BackupError):                     # Продолжение списка
            with self.subTest(exc=exc.__name__):                             # subTest для каждого
                self.assertTrue(issubclass(exc, StorageError))               # Потомок StorageError
                self.assertTrue(issubclass(exc, PhoneBookError))             # Потомок PhoneBookError

    def test_validation_errors(self):                                        # Тест ошибок валидации
        """Все ошибки валидации — потомки ValidationError и PhoneBookError."""  # Докстрока
        for exc in (EmptyFieldError, DuplicatePhoneError):                   # Перебираем классы
            with self.subTest(exc=exc.__name__):                             # subTest для каждого
                self.assertTrue(issubclass(exc, ValidationError))            # Потомок ValidationError
                self.assertTrue(issubclass(exc, PhoneBookError))             # Потомок PhoneBookError

    def test_direct_errors(self):                                            # Тест прямых потомков
        """ContactNotFoundError / InvalidContactIDError — прямые потомки."""  # Докстрока
        for exc in (ContactNotFoundError, InvalidContactIDError):            # Перебираем классы
            with self.subTest(exc=exc.__name__):                             # subTest для каждого
                self.assertTrue(issubclass(exc, PhoneBookError))             # Потомок PhoneBookError

    def test_exception_attributes(self):                                     # Тест атрибутов исключений
        """Атрибуты кастомных исключений сохраняются и видны в str()."""     # Докстрока
        err = EmptyFieldError("телефон")                                     # Создаём ошибку поля
        self.assertEqual(err.field, "телефон")                               # Атрибут сохранён
        self.assertIn("телефон", str(err))                                   # Текст содержит поле

        err2 = DuplicatePhoneError("+7999", 7)                               # Ошибка дубликата
        self.assertEqual(err2.phone, "+7999")                                # Телефон сохранён
        self.assertEqual(err2.cid, 7)                                        # ID сохранён
        self.assertIn("+7999", str(err2))                                    # Текст содержит телефон
        self.assertIn("ID=7", str(err2))                                     # Текст содержит ID

        err3 = ContactNotFoundError(42)                                      # Ошибка поиска
        self.assertEqual(err3.cid, 42)                                       # ID сохранён
        self.assertIn("42", str(err3))                                       # Текст содержит ID

        err4 = InvalidContactIDError("abc")                                  # Ошибка ID
        self.assertEqual(err4.raw, "abc")                                    # Сырой ввод сохранён
        self.assertIn("abc", str(err4))                                      # Текст содержит ввод


# =============================================================================
# PYTEST — фикстуры
# =============================================================================

@pytest.fixture                                                              # Декоратор фикстуры
def empty_book(tmp_path):                                                    # Фикстура пустой книги
    """Пустая книга во временной директории."""                              # Докстрока
    path = tmp_path / "contacts.txt"                                         # Путь к файлу
    return PhoneBook(str(path)), str(path)                                   # Возвращаем пару


@pytest.fixture                                                              # Декоратор фикстуры
def filled_book(tmp_path):                                                   # Фикстура заполненной книги
    """Книга с двумя контактами во временной директории."""                  # Докстрока
    path = tmp_path / "contacts.txt"                                         # Путь к файлу
    book = PhoneBook(str(path))                                              # Создаём книгу
    book.add("Иван", "Иванов", "+79990001122", "друг")                       # Первый контакт
    book.add("Пётр", "Петров", "+79993334455", "коллега")                    # Второй контакт
    return book, str(path)                                                   # Возвращаем пару


# =============================================================================
# PYTEST — базовые тесты с assert
# =============================================================================

def test_add_and_len(filled_book):                                           # Тест длины после добавления
    """Добавление через фикстуру даёт два контакта."""                       # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    assert len(book.contacts) == 2                                           # В книге 2 контакта


def test_add_returns_contact(empty_book):                                    # Тест возврата add
    """add возвращает контакт с корректными полями."""                       # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    c = book.add("A", "B", "+1")                                             # Добавляем контакт
    assert c.id == 1                                                         # Id == 1
    assert c.first == "A"                                                    # Имя совпало
    assert c.phone == "+1"                                                   # Телефон совпал


def test_search_by_name(filled_book):                                        # Тест поиска по имени
    """Поиск по имени."""                                                    # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    results = book.search("Иван", "имя")                                     # Ищем по имени
    assert len(results) == 1                                                 # Один результат
    assert results[0].first == "Иван"                                        # Нашли Ивана


def test_search_by_phone(filled_book):                                       # Тест поиска по телефону
    """Поиск по телефону."""                                                 # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    results = book.search("0001", "Номер")                                   # Ищем по номеру
    assert len(results) == 1                                                 # Один результат


def test_search_general(filled_book):                                        # Тест общего поиска
    """Общий поиск по комментарию."""                                        # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    results = book.search("коллега")                                         # Ищем без поля
    assert len(results) == 1                                                 # Один результат
    assert results[0].first == "Пётр"                                        # Нашли Петра


def test_update(filled_book):                                                # Тест обновления
    """Обновление полей контакта."""                                         # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    c = book.contacts[0]                                                     # Берём первый контакт
    book.update(c.id, first="Изменён", phone="+70000000000")                 # Обновляем
    assert c.first == "Изменён"                                              # Имя обновилось
    assert c.phone == "+70000000000"                                         # Телефон обновился


def test_delete(filled_book):                                                # Тест удаления
    """Удаление сокращает список на 1."""                                    # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    c = book.contacts[0]                                                     # Берём первый контакт
    book.delete(c.id)                                                        # Удаляем
    assert len(book.contacts) == 1                                           # Остался один


def test_save_load_roundtrip_pytest(tmp_path):                               # Тест roundtrip
    """save + PhoneBook = те же данные (pytest-версия)."""                   # Докстрока
    path = tmp_path / "contacts.txt"                                         # Путь к файлу
    book = PhoneBook(str(path))                                              # Новая книга
    book.add("A", "B", "+1", "x")                                            # Добавляем контакт
    book.save()                                                              # Сохраняем

    book2 = PhoneBook(str(path))                                             # Читаем обратно
    assert len(book2.contacts) == 1                                          # Один контакт
    assert book2.contacts[0].first == "A"                                    # Имя совпало
    assert book2.contacts[0].comment == "x"                                  # Комментарий совпал


def test_dirty_flag(empty_book):                                             # Тест флага dirty
    """dirty: False → True после add → False после save."""                  # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    assert not book.dirty                                                    # Изначально False
    book.add("A", "B", "+1")                                                 # Добавляем контакт
    assert book.dirty                                                        # Теперь True
    book.save()                                                              # Сохраняем
    assert not book.dirty                                                    # Снова False


# =============================================================================
# PYTEST — параметризация форматов данных
# =============================================================================

@pytest.mark.parametrize("first,last", [                                     # Параметризация имён
    ("Иван", "Иванов"),                                                      # Кириллица
    ("John", "Smith"),                                                       # Латиница
    ("Анна-Мария", "Петрова-Водкина"),                                       # Двойной дефис
    ("А", "Б"),                                                              # Одна буква
    ("Жанна", ""),                                                           # Только имя
    ("", "Толстой"),                                                         # Только фамилия
    ("О'Нил", "Макдональдс"),                                                # Апостроф
])                                                                           # Конец параметров
def test_add_various_name_formats(empty_book, first, last):                  # Тест форматов имён
    """Параметризация: разные форматы имён принимаются."""                   # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    c = book.add(first, last, "+70000000000")                                # Добавляем контакт
    assert c.first == first                                                  # Имя сохранено
    assert c.last == last                                                    # Фамилия сохранена


@pytest.mark.parametrize("phone", [                                          # Параметризация телефонов
    "+79990001122",                                                          # Компактный
    "+7 (999) 000-11-22",                                                    # Скобки и пробелы
    "8-999-000-11-22",                                                       # Дефисы, восьмёрка
    "9990001122",                                                            # Без плюса
    "+44 20 7946 0958",                                                      # Международный
    "+7 999 000 11 22",                                                      # Пробелы
    "8(999)000-11-22",                                                       # Смешанный
])                                                                           # Конец параметров
def test_add_various_phone_formats(empty_book, phone):                       # Тест форматов телефонов
    """Параметризация: разные форматы телефона принимаются."""               # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    c = book.add("Имя", "Фамилия", phone)                                    # Добавляем контакт
    assert c.phone == phone                                                  # Телефон сохранён


@pytest.mark.parametrize("field,query,expected_count", [                     # Параметризация поиска
    ("имя", "иван", 1),                                                      # Поиск по имени
    ("имя", "ИВАН", 1),                                                      # Регистронезависимо
    ("имя", "пётр", 1),                                                      # Поиск по имени (Пётр)
    ("фамилия", "иванов", 1),                                                # Поиск по фамилии
    ("фамилия", "петров", 1),                                                # Поиск по фамилии
    ("Номер", "+7999", 2),                                                   # Поиск по префиксу
    ("Номер", "0001", 1),                                                    # Поиск по фрагменту
    ("комментарий", "друг", 1),                                              # Поиск по комментарию
    ("комментарий", "коллега", 1),                                           # Поиск по комментарию
    ("комментарий", "нет-такого", 0),                                        # Ничего не найдено
])                                                                           # Конец параметров
def test_search_by_field_parametrized(filled_book, field, query, expected_count):  # Тест поиска
    """Параметризация: поиск по каждому полю с разными запросами."""         # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    assert len(book.search(query, field)) == expected_count                  # Сверяем количество


def test_search_empty_query_returns_all(filled_book):                        # Тест пустого запроса
    """Пустой запрос возвращает все контакты (текущее поведение)."""         # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    assert len(book.search("")) == 2                                         # Все контакты


@pytest.mark.parametrize("field_name,new_value,attr", [                      # Параметризация update
    ("first", "Новое", "first"),                                             # Обновление имени
    ("last", "Фам", "last"),                                                 # Обновление фамилии
    ("phone", "+70001112233", "phone"),                                      # Обновление телефона
    ("comment", "new-comment", "comment"),                                   # Обновление комментария
])                                                                           # Конец параметров
def test_update_individual_fields(filled_book, field_name, new_value, attr):  # Тест обновления поля
    """Параметризация: обновление каждого поля по отдельности."""            # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    c = book.contacts[0]                                                     # Берём первый контакт
    book.update(c.id, **{field_name: new_value})                             # Обновляем одно поле
    assert getattr(c, attr) == new_value                                     # Поле обновилось


# =============================================================================
# PYTEST — граничные условия
# =============================================================================

@pytest.mark.parametrize("bad_id", [0, -1, 999999])                          # Параметризация ID
def test_get_by_id_boundary(empty_book, bad_id):                             # Тест несуществующих ID
    """Граница: несуществующие ID (0, отрицательный, огромный)."""           # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    with pytest.raises(ContactNotFoundError):                                # Ожидаем ошибку
        book.get_by_id(bad_id)                                               # Пытаемся найти


def test_init_with_corrupted_file(tmp_path):                                 # Тест битого файла при init
    """Повреждённый файл при init — пустая книга без исключения."""          # Докстрока
    path = tmp_path / "bad.txt"                                              # Путь к файлу
    path.write_text("NOT A VALID LIST", encoding="utf-8")                    # Пишем мусор
    book = PhoneBook(str(path))                                              # Создаём книгу
    assert book.contacts == []                                               # Список пуст


def test_writer_backup_error_when_path_is_dir(tmp_path):                     # Тест BackupError
    """Если путь — директория, при save возникает BackupError."""            # Докстрока
    d = tmp_path / "not_a_file"                                              # Путь-директория
    d.mkdir()                                                                # Создаём директорию
    with pytest.raises(BackupError):                                         # Ожидаем ошибку
        ContactWriter.save([Contact(1, "A", "B", "+1")], str(d))             # Пытаемся сохранить


def test_writer_write_error(tmp_path):                                       # Тест ContactFileWriteError
    """Ошибка записи основного файла → ContactFileWriteError."""             # Докстрока
    path = tmp_path / "c.txt"                                                # Путь к файлу
    path.write_text("[]", encoding="utf-8")                                  # Создаём исходный файл
    real_open = open                                                         # Запоминаем настоящий open
    main_path = str(path)                                                    # Строковый путь

    def fake_open(file, mode="r", *args, **kwargs):                          # Замена open
        if "w" in mode and str(file) == main_path:                           # Запись основного файла
            raise OSError("test write failure")                              # Имитируем ошибку
        return real_open(file, mode, *args, **kwargs)                        # Остальное — как обычно

    with patch("builtins.open", side_effect=fake_open):                      # Подменяем open
        with pytest.raises(ContactFileWriteError):                           # Ожидаем ошибку
            ContactWriter.save([Contact(1, "A", "B", "+1")], main_path)      # Пытаемся сохранить


# =============================================================================
# PYTEST — проверки исключений
# =============================================================================

@pytest.mark.parametrize("first,last,phone", [                               # Параметризация
    ("", "", "+1"),                                                          # Нет имени и фамилии
    ("A", "B", ""),                                                          # Нет телефона
])                                                                           # Конец параметров
def test_add_invalid(empty_book, first, last, phone):                        # Тест невалидного add
    """Параметризация: невалидные входные данные — EmptyFieldError."""       # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    with pytest.raises(EmptyFieldError):                                     # Ожидаем ошибку
        book.add(first, last, phone)                                         # Пытаемся добавить


@pytest.mark.parametrize("query", ["zzz", "нет-такого", "Иван-не-то"])       # Параметризация запросов
def test_search_empty(filled_book, query):                                   # Тест пустого поиска
    """Параметризация: несуществующие запросы дают []."""                    # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    assert book.search(query) == []                                          # Результатов нет


def test_update_not_found_pytest(empty_book):                                # Тест update несуществующего
    """Обновление несуществующего — ContactNotFoundError."""                 # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    with pytest.raises(ContactNotFoundError):                                # Ожидаем ошибку
        book.update(999, first="A")                                          # Пытаемся обновить


def test_delete_not_found_pytest(empty_book):                                # Тест delete несуществующего
    """Удаление несуществующего — ContactNotFoundError."""                   # Докстрока
    book, _ = empty_book                                                     # Достаём книгу
    with pytest.raises(ContactNotFoundError):                                # Ожидаем ошибку
        book.delete(999)                                                     # Пытаемся удалить


def test_load_missing_file_pytest(tmp_path):                                 # Тест отсутствующего файла
    """Отсутствующий файл — ContactFileNotFoundError."""                     # Докстрока
    path = tmp_path / "missing.txt"                                          # Несуществующий путь
    with pytest.raises(ContactFileNotFoundError):                            # Ожидаем ошибку
        ContactReader.load(str(path))                                        # Пытаемся загрузить


def test_load_or_empty_missing_pytest(tmp_path):                             # Тест мягкой загрузки
    """Мягкая загрузка отсутствующего — []."""                               # Докстрока
    path = tmp_path / "missing.txt"                                          # Несуществующий путь
    assert ContactReader.load_or_empty(str(path)) == []                      # Пустой список


def test_from_dict_invalid_id_pytest():                                      # Тест некорректного Id
    """Некорректный Id — ContactFileFormatError."""                          # Докстрока
    with pytest.raises(ContactFileFormatError):                              # Ожидаем ошибку
        Contact.from_dict({                                                  # Пытаемся создать
            "Id": "abc", "имя": "A", "фамилия": "B",                         # Id строка
            "Номер": "+1", "комментарий": "",                                # Остальное корректно
        })                                                                   # Конец вызова


def test_add_duplicate_phone_pytest(filled_book):                            # Тест дубликата телефона
    """Дубликат телефона — DuplicatePhoneError."""                           # Докстрока
    book, _ = filled_book                                                    # Достаём книгу
    with pytest.raises(DuplicatePhoneError):                                 # Ожидаем ошибку
        book.add("Новый", "Контакт", "+79990001122")                         # Пытаемся добавить дубликат


def test_exception_attrs_pytest():                                           # Тест атрибутов исключений
    """Атрибуты исключений доступны напрямую."""                             # Докстрока
    assert EmptyFieldError("телефон").field == "телефон"                     # Поле сохранено
    assert DuplicatePhoneError("+1", 5).cid == 5                             # ID сохранён
    assert ContactNotFoundError(42).cid == 42                                # ID сохранён
    assert InvalidContactIDError("abc").raw == "abc"                         # Ввод сохранён


# =============================================================================
# Запуск unittest-тестов
# =============================================================================

if __name__ == "__main__":                                                   # Если запущен напрямую
    unittest.main()                                          