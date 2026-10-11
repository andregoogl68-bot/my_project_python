# my\_project\_python



Домашнее задание DZ\_1.



Исправлен Код Pyton в соответствии с замечаниями:



1\. Добавлены поля Id, Фамилия, Комментарий.

2\. Соответственно организован поиск по полям 'имя', 'фамилия', 'Номер', 'комментарий'

3\. Теперь в справочнике задействованы поля 'Id', 'имя', 'фамилия', 'Номер', 'комментарий'

4\. Добавил docstring к функциям и аннотации типов.

5\. добавить .gitignore.



Запускаете файл telfon\_spr\_V1.py



Подгружать Телефонный список из файла telefon\_V1.txt







Домашнее задание DZ\_2



1\.	Разбить код на 3 модуля: view, controller, model;



model.py больше ничего не печатает: методы add, update, delete, save возвращают результат (контакт или bool), а сообщения пользователю выводит контроллер через view.



view.py централизует весь ввод/вывод: печать таблицы, меню, запросы значений, ask\_int с защитой от нечислового ввода, confirm\_save.



controller.py содержит сценарии (edit\_contact, search\_menu, ask\_save\_on\_exit, load\_from\_file, main) и связывает модель и представление.



Точка входа — в controller.py, запуск: python controller.py. Модули должны лежать в одной папке (или быть пакетом), чтобы импорты from model import ... и import view работали.





2\.	Создать классы для справочника, контакта, чтения файла и записи файла;



Contact — теперь полноценный класс с атрибутами id, first, last, phone, comment.

Реализованы \_\_eq\_\_ (для сравнения со снимком в dirty), \_\_repr\_\_, clone, to\_dict, from\_dict.



ContactReader и ContactWriter — отдельные классы со статическими методами, отвечают строго за I/O.

PhoneBook больше не работает с файлами напрямую.



PhoneBook хранит list\[Contact], использует ContactReader/ContactWriter.

Появилось отображение SEARCH\_FIELDS, связывающее пользовательские имена полей (имя, фамилия, …) и атрибуты контакта.



view.py и controller.py переведены на работу с атрибутами (c.id, c.first, …) вместо ключей словаря.







3\.	Создать кастомные исключения для обработки всевозможных ошибок;



exceptions.py — единая иерархия с базой PhoneBookError.

Все ошибки делятся на три группы:

хранилище (StorageError),

валидация (ValidationError),

операции с контактами (ContactNotFoundError, InvalidContactIDError).

У каждой ошибки есть удобные атрибуты (field, phone, cid, raw) — контроллер при желании может их использовать.



model.py:



ContactReader.load теперь строгий:

возбуждает ContactFileNotFoundError / ContactFileFormatError.



Добавлен ContactReader.load\_or\_empty — мягкий режим для старта справочника.



ContactWriter.save возбуждает BackupError / ContactFileWriteError вместо «тихого» падения.



PhoneBook.get\_by\_id, update, delete возбуждают ContactNotFoundError вместо возврата None / False.



PhoneBook.add проверяет пустой телефон, пустые имя+фамилию и дубликат телефона.



PhoneBook.update проверяет дубликат телефона.





model.py:



Добавлена функция show\_error(error); ask\_int теперь возбуждает InvalidContactIDError.



controller.py:

главный цикл обёрнут в try/except PhoneBookError, поэтому любая ошибка показывается пользователю в формате \[Ошибка] … без падения программы. load\_from\_file использует строгий режим, чтобы сообщать о проблемах с явно указанным файлом.



Загружаете в Python файлы : controller.py, model.py, model.py, exceptions.py.



Запускаете управление из файла controller.py.



Подгружать Телефонный список из файла telefon\_V2.txt









