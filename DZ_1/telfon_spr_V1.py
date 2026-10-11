import ast                                                                                  # Импортируем модуль для безопасного преобразования строки в объект Python
from typing import Any, Optional                                                            # Импортируем типы для аннотаций

FILE_PATH: str = "contacts.txt"                                                             # Путь к файлу контактов по умолчанию

# Псевдоним типа для контакта: словарь со строковыми ключами и значениями любого типа
Contact = dict[str, Any]


def load_contacts(path: str) -> list[Contact]:
    """
    Загружает список контактов из файла.

    Файл должен содержать корректный (список словарей).
    Если файл отсутствует или повреждён, возвращается пустой список.

    :param path: Путь к файлу с контактами.
    :return: Список словарей-контактов с ключами
             'Id', 'имя', 'фамилия', 'Номер', 'комментарий'.
    """
    try:                                                                                    # Начинаем блок обработки исключений
        with open(path, "r", encoding="utf-8") as f:                                        # Открываем файл на чтение в UTF-8
            data: Any = ast.literal_eval(f.read())                                          # Безопасно преобразуем содержимое файла в объект Python
    except FileNotFoundError:                                                               # Если файл не найден
        return []                                                                           # Возвращаем пустой список
    except (SyntaxError, ValueError):                                                       # Если файл повреждён или имеет неверный формат
        return []                                                                           # Возвращаем пустой список
    contacts: list[Contact] = []                                                            # Создаём пустой список контактов
    for item in data:                                                                       # Перебираем элементы загруженного списка
        contacts.append({                                                                   # Добавляем нормализованный контакт
            "Id": int(item.get("Id", 0)),                                                   # ID приводим к целому числу
            "имя": item.get("имя", ""),                                                     # Имя по умолчанию пустое
            "фамилия": item.get("фамилия", ""),                                             # Фамилия по умолчанию пустая
            "Номер": item.get("Номер", ""),                                                 # Телефон по умолчанию пустой
            "комментарий": item.get("комментарий", ""),                                     # Комментарий по умолчанию пустой
        })                                                                                  # Закрываем словарь контакта
    return contacts                                                                         # Возвращаем список контактов


def save_contacts(contacts: list[Contact], path: str) -> None:
    """
    Сохраняет список контактов в файл с созданием резервной копии .bak.

    Перед перезаписью содержимое существующего файла копируется в файл
    с расширением .bak. Если исходного файла нет, копия не создаётся.

    :param contacts: Список словарей-контактов для сохранения.
    :param path: Путь к файлу, в который сохраняются контакты.
    :return: None
    """
    try:                                                                                    # Пытаемся создать резервную копию
        with open(path, "r", encoding="utf-8") as src:                                      # Открываем существующий файл
            backup: str = src.read()                                                        # Читаем его содержимое
        with open(path + ".bak", "w", encoding="utf-8") as dst:                             # Открываем .bak для записи
            dst.write(backup)                                                               # Записываем резервную копию
    except FileNotFoundError:                                                               # Если файла ещё нет
        pass                                                                                # Пропускаем создание копии
    with open(path, "w", encoding="utf-8") as f:                                            # Открываем файл для перезаписи
        f.write("[\n")                                                                      # Начинаем список
        for c in contacts:                                                                  # Перебираем контакты
            f.write(f"    {c!r},\n")                                                        # Записываем словарь в виде литерала Python
        f.write("]\n")                                                                      # Закрываем список


class PhoneBook:
    """Класс телефонного справочника с загрузкой, сохранением и поиском контактов."""

    def __init__(self, path: str = FILE_PATH) -> None:
        """
        Инициализирует телефонную книгу.

        :param path: Путь к файлу с контактами.
        :return: None
        """
        self.path: str = path                                                               # Сохраняем путь к файлу
        self.contacts: list[Contact] = load_contacts(path)                                  # Загружаем контакты из файла
        self.snapshot: list[Contact] = [dict(c) for c in self.contacts]                     # Делаем снимок для отслеживания изменений

    @property
    def dirty(self) -> bool:
        """
        Признак наличия несохранённых изменений.

        :return: True, если текущее состояние отличается от последнего сохранённого.
        """
        return self.contacts != self.snapshot                                               # Сравниваем текущие контакты со снимком

    def save(self) -> None:
        """
        Сохраняет текущее состояние книги на диск и обновляет снимок.

        :return: None
        """
        save_contacts(self.contacts, self.path)                                             # Сохраняем контакты на диск
        self.snapshot = [dict(c) for c in self.contacts]                                    # Обновляем снимок
        print("Сохранено.")                                                                 # Сообщаем пользователю

    def next_id(self) -> int:
        """
        Возвращает следующий свободный идентификатор контакта.

        :return: Максимальный существующий ID + 1, либо 1, если контактов нет.
        """
        return max((c["Id"] for c in self.contacts), default=0) + 1                         # Возвращаем максимальный ID + 1

    def get_by_id(self, cid: int) -> Optional[Contact]:
        """
        Ищет контакт по идентификатору.

        :param cid: Идентификатор контакта.
        :return: Словарь-контакт или None, если контакт не найден.
        """
        for c in self.contacts:                                                             # Перебираем контакты
            if c["Id"] == cid:                                                              # Если ID совпал
                return c                                                                    # Возвращаем контакт
        return None                                                                         # Если контакт не найден

    def add(self, first: str, last: str, phone: str, comment: str = "") -> None:
        """
        Добавляет новый контакт в книгу.

        :param first: Имя контакта.
        :param last: Фамилия контакта.
        :param phone: Номер телефона.
        :param comment: Комментарий (по умолчанию пустая строка).
        :return: None
        """
        self.contacts.append({                                                              # Добавляем новый контакт в список
            "Id": self.next_id(),                                                           # Новый ID
            "имя": first,                                                                   # Имя
            "фамилия": last,                                                                # Фамилия
            "Номер": phone,                                                                 # Телефон
            "комментарий": comment,                                                         # Комментарий
        })                                                                                  # Закрываем словарь
        print("Контакт добавлен.")                                                          # Сообщаем пользователю

    def update(self, cid: int, **fields: str) -> None:
        """
        Обновляет поля существующего контакта.

        Пустые значения игнорируются (поле не меняется).

        :param cid: Идентификатор контакта.
        :param fields: Произвольный набор полей для обновления
                       (например, имя="Иван", Номер="+7...").
        :return: None
        """
        c: Optional[Contact] = self.get_by_id(cid)                                          # Находим контакт по ID
        if not c:                                                                           # Если контакт не найден
            print("Контакт не найден.")                                                     # Сообщаем пользователю
            return                                                                          # Выходим из метода
        for key, value in fields.items():                                                   # Перебираем переданные поля
            if value:                                                                       # Если значение не пустое
                c[key] = value                                                              # Обновляем поле контакта
        print("Контакт изменён.")                                                           # Сообщаем пользователю

    def delete(self, cid: int) -> None:
        """
        Удаляет контакт по идентификатору.

        :param cid: Идентификатор контакта.
        :return: None
        """
        c: Optional[Contact] = self.get_by_id(cid)                                          # Находим контакт по ID
        if not c:                                                                           # Если контакт не найден
            print("Контакт не найден.")                                                     # Сообщаем пользователю
            return                                                                          # Выходим из метода
        self.contacts.remove(c)                                                             # Удаляем контакт из списка
        print("Контакт удалён.")                                                            # Сообщаем пользователю

    def search(self, query: str, field: Optional[str] = None) -> list[Contact]:
        """
        Ищет контакты по подстроке.

        :param query: Поисковый запрос (регистр не учитывается).
        :param field: Имя поля для поиска. Если None — поиск по всем полям.
        :return: Список найденных контактов.
        """
        q: str = query.lower()                                                              # Приводим запрос к нижнему регистру
        result: list[Contact] = []                                                          # Создаём список результатов
        for c in self.contacts:                                                             # Перебираем контакты
            if field:                                                                       # Если указано конкретное поле
                if q in str(c[field]).lower():                                              # Ищем подстроку в поле
                    result.append(c)                                                        # Добавляем контакт в результаты
            else:                                                                           # Если поле не указано
                if any(q in str(v).lower() for v in c.values()):                            # Ищем по всем значениям
                    result.append(c)                                                        # Добавляем контакт в результаты
        return result                                                                       # Возвращаем список найденных контактов

    def print_contacts(self, contacts: Optional[list[Contact]] = None) -> None:
        """
        Выводит контакты в виде таблицы.

        :param contacts: Список контактов для вывода. Если None — выводятся все контакты.
        :return: None
        """
        if contacts is None:                                                                # Если список не передан
            contacts = self.contacts                                                        # Берём все контакты
        if not contacts:                                                                    # Если контактов нет
            print("Контактов нет.")                                                         # Сообщаем пользователю
            return                                                                          # Выходим из метода
        print(f"\n{'ID':<4} {'Имя':<12} {'Фамилия':<14} {'Телефон':<20} Комментарий")       # Печатаем заголовок
        print("-" * 80)                                                                     # Печатаем разделитель
        for c in contacts:                                                                  # Перебираем контакты
            print(f"{c['Id']:<4} {c['имя']:<12} {c['фамилия']:<14} {c['Номер']:<20} {c['комментарий']}")  # Печатаем строку


def edit_contact(book: PhoneBook) -> None:
    """
    Интерактивно редактирует контакт по ID.

    Пустая строка в любом поле означает «оставить без изменений».

    :param book: Экземпляр PhoneBook.
    :return: None
    """
    book.print_contacts()                                                                   # Показываем список контактов
    try:                                                                                    # Пытаемся прочитать ID
        cid: int = int(input("ID контакта: "))                                              # Вводим ID и преобразуем в число
    except ValueError:                                                                      # Если введено не число
        print("ID должен быть числом.")                                                     # Сообщаем пользователю
        return                                                                              # Выходим из функции
    c: Optional[Contact] = book.get_by_id(cid)                                              # Находим контакт по ID
    if not c:                                                                               # Если контакт не найден
        print("Контакт не найден.")                                                         # Сообщаем пользователю
        return                                                                              # Выходим из функции
    print("Пустое поле — не менять.")                                                       # Подсказываем пользователю
    first: str = input(f"Имя [{c['имя']}]: ").strip()                                       # Вводим новое имя
    last: str = input(f"Фамилия [{c['фамилия']}]: ").strip()                                # Вводим новую фамилию
    phone: str = input(f"Телефон [{c['Номер']}]: ").strip()                                 # Вводим новый телефон
    comment: str = input(f"Комментарий [{c['комментарий']}]: ").strip()                     # Вводим новый комментарий
    book.update(cid, имя=first, фамилия=last, Номер=phone, комментарий=comment)             # Обновляем контакт


def search_menu(book: PhoneBook) -> None:
    """
    Меню поиска контактов по выбранному полю.

    :param book: Экземпляр PhoneBook.
    :return: None
    """
    print("\n1-имя  2-фамилия  3-телефон  4-комментарий  5-общий поиск")                    # Печатаем меню поиска
    choice: str = input("Пункт: ").strip()                                                  # Вводим пункт меню
    fields: dict[str, Optional[str]] = {                                                    # Соответствие пунктов и полей
        "1": "имя",
        "2": "фамилия",
        "3": "Номер",
        "4": "комментарий",
        "5": None,
    }
    if choice not in fields:                                                                # Если пункт неверный
        print("Неверный пункт.")                                                            # Сообщаем пользователю
        return                                                                              # Выходим из функции
    query: str = input("Запрос: ").strip()                                                  # Вводим поисковый запрос
    results: list[Contact] = book.search(query, fields[choice])                             # Ищем контакты
    print(f"Найдено: {len(results)}")                                                       # Печатаем количество найденных
    book.print_contacts(results)                                                            # Печатаем найденные контакты


def ask_save_on_exit(book: PhoneBook) -> None:
    """
    Предлагает сохранить несохранённые изменения при выходе.

    :param book: Экземпляр PhoneBook.
    :return: None
    """
    if not book.dirty:                                                                      # Если изменений нет
        return                                                                              # Ничего не делаем
    answer: str = input("Есть несохранённые изменения. Сохранить? (y/n): ").strip().lower() # Спрашиваем пользователя
    if answer in ("y", "yes", "д", "да"):                                                   # Если ответ положительный
        book.save()                                                                         # Сохраняем книгу


def main() -> None:
    """
    Точка входа: запускает интерактивное меню телефонного справочника.

    :return: None
    """
    book: PhoneBook = PhoneBook()                                                           # Создаём телефонную книгу

    menu: str = (                                                                           # Начинаем формирование текста меню
        "\n=== Телефонный справочник ===\n"                                                 # Заголовок меню
        "1. Показать контакты\n"                                                            # Пункт 1
        "2. Добавить\n"                                                                     # Пункт 2
        "3. Редактировать\n"                                                                # Пункт 3
        "4. Удалить\n"                                                                      # Пункт 4
        "5. Поиск\n"                                                                        # Пункт 5
        "6. Сохранить\n"                                                                    # Пункт 6
        "7. Загрузить из файла\n"                                                           # Пункт 7
        "0. Выход"                                                                          # Пункт 0
    )                                                                                       # Заканчиваем формирование меню

    while True:                                                                             # Бесконечный цикл работы программы
        print(menu)                                                                         # Печатаем меню
        choice: str = input("Ваш выбор: ").strip()                                          # Вводим выбор пользователя

        if choice == "1":                                                                   # Если выбран пункт 1
            book.print_contacts()                                                           # Показываем контакты
        elif choice == "2":                                                                 # Если выбран пункт 2
            first: str = input("Имя: ").strip()                                             # Вводим имя
            last: str = input("Фамилия: ").strip()                                          # Вводим фамилию
            phone: str = input("Телефон: ").strip()                                         # Вводим телефон
            comment: str = input("Комментарий: ").strip()                                   # Вводим комментарий
            book.add(first, last, phone, comment)                                           # Добавляем контакт
        elif choice == "3":                                                                 # Если выбран пункт 3
            edit_contact(book)                                                              # Редактируем контакт
        elif choice == "4":                                                                 # Если выбран пункт 4
            book.print_contacts()                                                           # Показываем контакты
            try:                                                                            # Пытаемся прочитать ID
                cid: int = int(input("ID контакта: "))                                      # Вводим ID и преобразуем в число
                book.delete(cid)                                                            # Удаляем контакт
            except ValueError:                                                              # Если введено не число
                print("ID должен быть числом.")                                             # Сообщаем пользователю
        elif choice == "5":                                                                 # Если выбран пункт 5
            search_menu(book)                                                               # Открываем меню поиска
        elif choice == "6":                                                                 # Если выбран пункт 6
            book.save()                                                                     # Сохраняем книгу
        elif choice == "7":                                                                 # Если выбран пункт 7
            ask_save_on_exit(book)                                                          # Предлагаем сохранить текущие изменения перед загрузкой
            filename: str = input("Имя файла для загрузки: ").strip()                       # Вводим имя файла
            book.path = filename                                                            # Запоминаем новый путь к файлу
            book.contacts = load_contacts(filename)                                         # Загружаем контакты из файла
            book.snapshot = [dict(c) for c in book.contacts]                                # Обновляем снимок
            print(f"Загружено контактов: {len(book.contacts)}")                             # Сообщаем количество загруженных
        elif choice == "0":                                                                 # Если выбран пункт 0
            ask_save_on_exit(book)                                                          # Предлагаем сохранить изменения
            print("До свидания.")                                                           # Прощаемся с пользователем
            break                                                                           # Выходим из цикла
        else:                                                                               # Если выбран неизвестный пункт
            print("Неверный пункт.")                                                        # Сообщаем пользователю


if __name__ == "__main__":                                                                  # Проверяем, запущен ли файл как основная программа
    main()                                                                                  # Запускаем главную функцию