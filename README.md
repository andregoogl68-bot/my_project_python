# my\_project\_python
# PhoneBook Python — телефонный справочник

Учебный проект на Python: консольный телефонный справочник.
Каждое домашнее задание хранится в отдельной папке:

- **DZ_1** — монолитная версия;
- **DZ_2** — модульная версия с классами и кастомными исключениями;
- **DZ_3** — покрытие тестами (unittest + pytest) и настройка IDE.

## Содержание

- [О проекте](#о-проекте)
- [Структура проекта](#структура-проекта)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [DZ_1](#dz_1)
- [DZ_2](#dz_2)
- [DZ_3](#dz_3)
- [Корректировки DZ_2](#корректировки-dz_2)
- [Архитектура](#архитектура)
- [Исключения](#исключения)
- [Тестирование](#тестирование)
- [Формат данных](#формат-данных)
- [Примечания](#примечания)

## О проекте

Телефонный справочник с возможностью:

- добавлять контакты;
- редактировать контакты;
- удалять контакты;
- искать по полям;
- сохранять и загружать данные из текстового файла.

По мере развития проекта требования усложнялись, поэтому код разделён на три независимых папки — по одной на каждое домашнее задание.

| Папка | Что внутри |
|---|---|
| `DZ_1` | монолитная программа `telfon_spr_V1.py` + `contacts.txt` |
| `DZ_2` | модульный проект: `controller.py`, `model.py`, `view.py`, `exceptions.py` + `contacts.txt` |
| `DZ_3` | тесты `test_directory.py` + настройки IDE `pyrightconfig.json` и `zzz_probe.py` |

## Структура проекта
my_project_python/
├── README.md
│
├── DZ_1/
│ ├── telfon_spr_V1.py # монолитная версия программы
│ ├── contacts.txt # данные справочника
│ └── .gitignore
│
├── DZ_2/
│ ├── controller.py # точка входа, сценарии работы
│ ├── model.py # Contact, PhoneBook, ContactReader, ContactWriter
│ ├── view.py # весь ввод/вывод, меню, таблицы
│ ├── exceptions.py # иерархия кастомных исключений
│ ├── contacts.txt # данные справочника
│ └── .gitignore
│
└── DZ_3/
├── controller.py # копия модулей DZ_2 (все в одной папке)
├── model.py
├── view.py
├── exceptions.py
├── test_directory.py # тесты: unittest + pytest
├── pyrightconfig.json # настройки Pylance для корректной индексации
├── zzz_probe.py # диагностический файл для проверки Pylance
├── contacts.txt
└── .gitignore

> В `DZ_3` все модули (`controller.py`, `model.py`, `view.py`, `exceptions.py`) лежат в одной папке — так требуют импорты и так удобнее запускать тесты.

## Требования

- **Python 3.10 или выше.**
  Проект проверен на **Python 3.14.5** (Windows, Python Install Manager).
- Дополнительные библиотеки для запуска приложения не требуются.
- Для тестов нужен `pytest` (см. [Тестирование](#тестирование)).

## Установка

```
git clone <URL-репозитория>
cd my_project_python

Если виртуальное окружение не требуется, можно сразу переходить к запуску нужного ДЗ.

Использование
Запуск выполняется из папки соответствующего домашнего задания.

DZ_1

cd DZ_1
python telfon_spr_V1.py
Данные загружаются из DZ_1/contacts.txt

DZ_2

cd DZ_2
python controller.py
Данные загружаются из DZ_2/contacts.txt.

DZ_3

cd DZ_3
python controller.py                         # обычный запуск
python test_directory.py                     # тесты (unittest)
python -m pytest test_directory.py -v        # тесты (unittest + pytest)
Данные загружаются из DZ_3/contacts.txt.

DZ_1
Монолитная версия программы. Всё в одном файле telfon_spr_V1.py.

Что реализовано:

поля контакта: Id, имя, фамилия, Номер, комментарий;

поиск по полям: имя, фамилия, номер, комментарий;

CRUD-операции;

сохранение и загрузка из contacts.txt;

docstring и аннотации типов;

.gitignore.

Запуск:

cd DZ_1
python telfon_spr_V1.py

DZ_2
Модульная версия. Код разбит на model.py, view.py, controller.py, добавлен exceptions.py.

Что реализовано:

model.py — бизнес-логика, ничего не печатает:

Contact с атрибутами id, first, last, phone, comment;

методы to_dict, from_dict, clone, __eq__, __repr__;

PhoneBook — справочник контактов;

ContactReader — чтение из файла (строгий и мягкий режимы);

ContactWriter — запись с резервной копией .bak;

SEARCH_FIELDS — соответствие пользовательских имён полей и атрибутов.

view.py — весь ввод/вывод:

печать таблиц и меню;

ask, ask_int (возбуждает InvalidContactIDError);

confirm_save, show_error.

controller.py — сценарии работы:

edit_contact, search_menu, ask_save_on_exit, load_from_file, main;

главный цикл обёрнут в try/except PhoneBookError — ошибки показываются как [Ошибка] ..., программа не падает.

exceptions.py — иерархия исключений с базой PhoneBookError (см. Исключения).

Валидация в PhoneBook.add:

пустой телефон;

пустые имя и фамилия;

дубликат телефона.

PhoneBook.update дополнительно проверяет дубликат телефона.

Запуск:

cd DZ_2
python controller.py

DZ_3

Тестовое покрытие и настройка IDE. В папке DZ_3/ лежат копии модулей из DZ_2 (все в одной папке), плюс три новых файла.

test_directory.py — тесты
Содержит два набора:

unittest — классы-наследники TestCase, setUp/tearDown, assertEqual, assertRaises, assertRaisesRegex, subTest;

pytest — фикстуры, параметризация, pytest.raises.

Покрытие:

Contact: to_dict, from_dict, clone, __eq__, разные варианты Id;

ContactReader: отсутствие файла, пустой/валидный/битый файл, не-список, не-словарь, load_or_empty;

ContactWriter: сохранение пустого/одного контакта, создание .bak, ошибки записи (BackupError, ContactFileWriteError);

PhoneBook: add, search (по всем полям), update, delete, next_id, dirty, roundtrip save/load;

view: ask, ask_int, confirm_save, вывод через redirect_stdout;

иерархия исключений и их атрибуты;

граничные условия: пустой контакт, только имя/только фамилия, несуществующие ID (0, -1, огромный), пустой поисковый запрос, битый файл при init;

параметризация: разные форматы имён, телефонов, поля поиска и обновления.

Запуск:


cd DZ_3
python test_directory.py                     # unittest
python -m pytest test_directory.py -v        # unittest + pytest
Установка pytest (если ещё не установлен):


python -m pip install pytest
pyrightconfig.json — настройки Pylance
Файл устраняет конфликт между версией интерпретатора и Pylance. Из-за рассинхронизации версии Python Pylance мог не видеть builtins (open, print, len) и stdlib, что давало десятки ложных ошибок reportUndefinedVariable в test_directory.py.

json
{
    "include": ["."],
    "exclude": ["**/__pycache__", "**/*.bak", "**/htmlcov", "**/.pytest_cache"],
    "pythonVersion": "3.14",
    "typeCheckingMode": "basic",
    "reportMissingImports": "warning",
    "reportUndefinedVariable": "warning"
}
При смене интерпретатора Python не забудьте синхронизировать строку pythonVersion — иначе Pylance снова начнёт подчёркивать builtins.

zzz_probe.py — диагностический файл
Маленький файл для проверки, видит ли Pylance встроенные функции:

python
print(open)
print(print)
print(len)

x: dict[str, int] = {}
Если в этом файле Pylance подчёркивает open/print/len — проблема глобальная (в интерпретаторе или настройках). Если чисто — проблема локальная, в конкретном файле. Использовался при отладке Pylance, после решения конфликта можно удалить — на работу приложения он не влияет.

Запуск:


cd DZ_3
python zzz_probe.py
Ожидаемый вывод:

text
<built-in function open>
<built-in function print>
<built-in function len>
Корректировки DZ_2
По замечаниям к DZ_2 внесены три правки.

1. Имя файла по умолчанию
Путь по умолчанию в model.py (FILE_PATH) — contacts.txt. Файл telefon_V2.txt переименован в contacts.txt, чтобы при запуске загружались существующие контакты и не было расхождений между именем файла в коде и в проекте.

2. Обработка ошибок в Contact.from_dict()
Раньше вызов int(data.get("Id", 0)) мог возбудить ValueError/TypeError при некорректных данных в файле. Теперь:

вызов обёрнут в try/except (ValueError, TypeError);

при ошибке возбуждается ContactFileFormatError с сообщением, содержащим исходное значение Id, и from e для сохранения исходного исключения;

в докстроку добавлена строка :raises ContactFileFormatError: если значение 'Id' не является целым числом.;

остальной код метода (cls(...)) не изменился — используется уже проверенный cid.

3. Сохранение при загрузке другого файла
В controller.py при загрузке другого файла текущие несохранённые изменения терялись без предупреждения. Теперь в начале load_from_file() вызывается ask_save_on_exit(book):

если book.dirty — пользователя спрашивают, сохранить ли изменения;

если пользователь отвечает «да» — вызывается book.save();

в докстроку добавлено «Перед загрузкой предлагает сохранить несохранённые изменения.» и уточнение :raises: («…либо сохранение не удалось»).

Архитектура
Описывает модульную версию (DZ_2 и DZ_3).

model.py
Бизнес-логика и работа с данными. Не печатает сообщения пользователю.

Основные классы:

Contact — контакт с атрибутами id, first, last, phone, comment.

PhoneBook — справочник контактов.

ContactReader — чтение из файла.

ContactWriter — запись в файл.

SEARCH_FIELDS — соответствие пользовательских названий полей и атрибутов контакта.

Методы add, update, delete, save возвращают результат — Contact или bool. Сообщения выводит контроллер через view.

view.py
Централизует весь ввод и вывод:

печать таблицы контактов;

вывод меню;

запрос значений (ask);

ask_int с защитой от нечислового ввода (возбуждает InvalidContactIDError);

confirm_save;

show_error.

controller.py
Сценарии работы приложения:

edit_contact;

search_menu;

ask_save_on_exit;

load_from_file;

main.

Главный цикл обёрнут в try/except PhoneBookError, поэтому ошибки показываются пользователю в формате [Ошибка] ... и программа не завершается аварийно.

exceptions.py
Единая иерархия исключений с базовым классом PhoneBookError.

Исключения
Все ошибки делятся на три группы.

Хранилище — StorageError:

ContactFileNotFoundError;

ContactFileFormatError;

ContactFileWriteError;

BackupError.

Валидация — ValidationError:

EmptyFieldError;

DuplicatePhoneError.

Операции с контактами:

ContactNotFoundError;

InvalidContactIDError.

У исключений есть удобные атрибуты: field, phone, cid, raw. Контроллер может использовать их при обработке ошибок.

Тестирование
Тесты находятся в DZ_3/test_directory.py и содержат оба набора — unittest и pytest.

Запуск только unittest:


cd DZ_3
python test_directory.py
Запуск unittest + pytest:


cd DZ_3
python -m pytest test_directory.py -v
Установка pytest (если ещё не установлен):


python -m pip install pytest
Что покрыто тестами:

Contact, ContactReader, ContactWriter, PhoneBook, view;

все кастомные исключения, включая BackupError и ContactFileWriteError;

иерархия исключений и их атрибуты;

граничные условия: пустой контакт, только имя/только фамилия, несуществующие ID (0, -1, огромный), пустой поисковый запрос, битый файл при init;

параметризация: разные форматы имён, телефонов, поля поиска и обновления.

Настройка Pylance. В DZ_3/pyrightconfig.json зафиксирован pythonVersion: "3.14". При смене интерпретатора Python не забудьте синхронизировать эту строку. Для быстрой проверки, видит ли Pylance builtins, есть DZ_3/zzz_probe.py.

Формат данных
В каждой папке — свой contacts.txt (данные не пересекаются между ДЗ).

Формат — литерал Python-списка словарей:

python
[
    {'Id': 1, 'имя': 'Иван', 'фамилия': 'Иванов', 'Номер': '+79990001122', 'комментарий': 'друг'},
    {'Id': 2, 'имя': 'Пётр', 'фамилия': 'Петров', 'Номер': '+79993334455', 'комментарий': 'коллега'},
]
Поля контакта: Id, имя, фамилия, Номер, комментарий.

В модульной версии (DZ_2, DZ_3) чтение и запись выполняются классами ContactReader и ContactWriter через ast.literal_eval (безопасно, без исполнения кода). При сохранении создаётся резервная копия contacts.txt.bak