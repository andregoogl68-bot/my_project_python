import view                                                                  # Импортируем модуль представления

from exceptions import PhoneBookError                                        # Импортируем базовое кастомное исключение
from model import ContactReader, PhoneBook                                   # Импортируем модель и класс чтения файла


def edit_contact(book: PhoneBook) -> None:
    """
    Интерактивно редактирует контакт по ID.

    Пустая строка в любом поле означает «оставить без изменений».

    :param book: Экземпляр PhoneBook.
    :raises PhoneBookError: при ошибках поиска, обновления или валидации.
    :return: None
    """
    view.show_contacts(book.contacts)                                        # Показываем список контактов
    cid = view.ask_int("ID контакта: ")                                      # Запрашиваем ID (может возбудить исключение)
    c = book.get_by_id(cid)                                                  # Находим контакт (может возбудить исключение)
    view.show_message("Пустое поле — не менять.")                            # Подсказываем пользователю
    first = view.ask(f"Имя [{c.first}]: ")                                   # Вводим новое имя
    last = view.ask(f"Фамилия [{c.last}]: ")                                 # Вводим новую фамилию
    phone = view.ask(f"Телефон [{c.phone}]: ")                               # Вводим новый телефон
    comment = view.ask(f"Комментарий [{c.comment}]: ")                       # Вводим новый комментарий
    book.update(cid, first=first, last=last, phone=phone, comment=comment)   # Обновляем контакт (может возбудить исключение)
    view.show_message("Контакт изменён.")                                    # Сообщаем пользователю


def search_menu(book: PhoneBook) -> None:
    """
    Меню поиска контактов по выбранному полю.

    :param book: Экземпляр PhoneBook.
    :return: None
    """
    view.show_search_menu()                                                  # Печатаем меню поиска
    choice = view.ask("Пункт: ")                                             # Вводим пункт меню
    fields = {                                                               # Соответствие пунктов и полей
        "1": "имя",
        "2": "фамилия",
        "3": "Номер",
        "4": "комментарий",
        "5": None,
    }
    if choice not in fields:                                                 # Если пункт неверный
        view.show_message("Неверный пункт.")                                 # Сообщаем пользователю
        return                                                               # Выходим из функции
    query = view.ask("Запрос: ")                                             # Вводим поисковый запрос
    results = book.search(query, fields[choice])                             # Ищем контакты в модели
    view.show_message(f"Найдено: {len(results)}")                            # Печатаем количество найденных
    view.show_contacts(results)                                              # Печатаем найденные контакты


def ask_save_on_exit(book: PhoneBook) -> None:
    """
    Предлагает сохранить несохранённые изменения при выходе.

    :param book: Экземпляр PhoneBook.
    :raises PhoneBookError: если сохранение не удалось.
    :return: None
    """
    if not book.dirty:                                                       # Если изменений нет
        return                                                               # Ничего не делаем
    if view.confirm_save():                                                  # Спрашиваем пользователя
        book.save()                                                          # Сохраняем книгу (может возбудить исключение)
        view.show_message("Сохранено.")                                      # Сообщаем пользователю


def load_from_file(book: PhoneBook) -> None:
    """
    Загружает контакты из указанного пользователем файла (строгий режим).

    :param book: Экземпляр PhoneBook.
    :raises PhoneBookError: если файл не найден или повреждён.
    :return: None
    """
    filename = view.ask("Имя файла для загрузки: ")                          # Вводим имя файла
    contacts = ContactReader.load(filename)                                  # Загружаем (может возбудить исключение)
    book.path = filename                                                     # Запоминаем новый путь к файлу
    book.contacts = contacts                                                 # Подменяем список контактов
    book.snapshot = [c.clone() for c in contacts]                            # Обновляем снимок
    view.show_message(f"Загружено контактов: {len(contacts)}")               # Сообщаем количество загруженных


def main() -> None:
    """
    Точка входа: запускает интерактивное меню телефонного справочника.

    :return: None
    """
    book = PhoneBook()                                                       # Создаём телефонную книгу

    while True:                                                              # Бесконечный цикл работы программы
        view.show_main_menu()                                                # Печатаем главное меню
        choice = view.ask("Ваш выбор: ")                                     # Вводим выбор пользователя

        try:                                                                 # Обрабатываем возможные ошибки
            if choice == "1":                                                # Показать контакты
                view.show_contacts(book.contacts)                            # Отображаем все контакты
            elif choice == "2":                                              # Добавить
                first = view.ask("Имя: ")                                    # Вводим имя
                last = view.ask("Фамилия: ")                                 # Вводим фамилию
                phone = view.ask("Телефон: ")                                # Вводим телефон
                comment = view.ask("Комментарий: ")                          # Вводим комментарий
                book.add(first, last, phone, comment)                        # Добавляем контакт (может возбудить исключение)
                view.show_message("Контакт добавлен.")                       # Сообщаем пользователю
            elif choice == "3":                                              # Редактировать
                edit_contact(book)                                           # Редактируем контакт
            elif choice == "4":                                              # Удалить
                view.show_contacts(book.contacts)                            # Показываем контакты
                cid = view.ask_int("ID контакта: ")                          # Запрашиваем ID
                book.delete(cid)                                             # Удаляем контакт (может возбудить исключение)
                view.show_message("Контакт удалён.")                         # Сообщаем об успехе
            elif choice == "5":                                              # Поиск
                search_menu(book)                                            # Открываем меню поиска
            elif choice == "6":                                              # Сохранить
                book.save()                                                  # Сохраняем книгу (может возбудить исключение)
                view.show_message("Сохранено.")                              # Сообщаем пользователю
            elif choice == "7":                                              # Загрузить из файла
                load_from_file(book)                                         # Загружаем контакты
            elif choice == "0":                                              # Выход
                ask_save_on_exit(book)                                       # Предлагаем сохранить изменения
                view.show_message("До свидания.")                            # Прощаемся с пользователем
                break                                                        # Выходим из цикла
            else:                                                            # Неизвестный пункт
                view.show_message("Неверный пункт.")                         # Сообщаем пользователю
        except PhoneBookError as e:                                          # Ловим любое кастомное исключение справочника
            view.show_error(e)                                               # Показываем пользователю текст ошибки


if __name__ == "__main__":                                                   # Проверяем, запущен ли файл как основная программа
    main()                                                                   # Запускаем главную функцию