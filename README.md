# pinterest-qa-lab

Лабораторна робота «Комплексне застосування методів забезпечення якості ПЗ».
Об'єкт тестування: **Pinterest Web** (https://www.pinterest.com).

Виконала: Величко Діана Сергіївна, Київський національний університет імені Тараса Шевченка, факультет комп'ютерних наук та кібернетики.

Стек автотестів: Python 3.9+, Playwright, pytest, pytest-html, шаблон **Page Object Model**.

---

## 1. Відповідність завданням лабораторної

| № | Завдання | Де знаходиться |
|---|---|---|
| 1 | Специфікація вимог (SRS) | Звіт `QA_lab_Velychko.docx`, розділ 1 |
| 2 | Тест-план (цілі, обсяг, ресурси й ролі, ризики, критерії) | Звіт, розділ 2 |
| 3 | Чек-лист | Звіт, розділ 3 (і таблиця Google Sheets) |
| 4 | Тест-кейси (TC-01 … TC-21) | Звіт, розділ 4 (і таблиця Google Sheets) |
| 5 | Юзабіліті-тестування | `docs/Частина_5_Юзабіліті_тестування_Pinterest.docx` |
| 6 | Автоматизація тест-кейсів | Цей репозиторій (`pages/`, `tests/`) |
| 7 | Презентація результатів | `docs/presentation.pptx` (додати перед здачею) |

Примітка щодо Частини 5: дані респондентів змодельовані й у документі це прямо позначено; експертна оцінка виконана за евристиками Нільсена та за публічними відгуками користувачів.

---

## 2. Структура проєкту

```
pinterest-qa-lab/
├── config/settings.py          # налаштування з .env (email, пароль, дошка, URL)
├── pages/                      # Page Object
│   ├── base_page.py
│   ├── login_page.py
│   ├── signup_page.py
│   ├── search_page.py
│   ├── home_page.py
│   ├── board_page.py
│   ├── pin_builder_page.py
│   └── components/pin_grid.py  # спільний компонент сітки пінів (DRY)
├── tests/
│   ├── conftest.py             # фікстури, порядок виконання, сесії
│   ├── test_auth.py            # TC-03, 04, 05, 07, 08, 10
│   ├── test_search.py          # TC-11, 12, 13, 15
│   └── test_pins_boards.py     # TC-18, 19, 20, 21
├── utils/helpers.py            # унікальні імена, тестове зображення
├── save_auth.py                # ручне збереження сесій входу
├── run_all.py                  # запуск усіх етапів по черзі
├── pytest.ini
├── requirements.txt
├── .env.example
├── auth/                       # збережені сесії                 
└── reports/  
```

Застосовані практики: Page Object Model, параметризація (DDT) у TC-03/04/11, винесений компонент `PinGrid` (DRY), централізовані локатори, збережений стан сесії (`storage_state`) замість повторних входів, `xfail` для відомої розбіжності зі специфікацією.

---

## 3. Налаштування

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium webkit
cp .env.example .env
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium webkit
copy .env.example .env
```

Заповнити `.env`:

```
BASE_URL=https://www.pinterest.com
PINTEREST_EMAIL=тестовий_акаунт@example.com
PINTEREST_PASSWORD=пароль
PINTEREST_BOARD=назва_існуючої_дошки
DEFAULT_TIMEOUT_MS=15000
```

Використовувати тестовий акаунт. Файл `.env` у git не потрапляє.

---

## 4. Запуск тестів

Pinterest блокує часті автоматичні входи (CAPTCHA), тому логін виконується вручну один раз, а тести використовують збережену сесію.

> У zsh не пиши коментарі `# …` в одному рядку з командою. Кожну команду виконуй окремо.

**Крок 1. Збережи сесії** (відкриється браузер, увійди; потрібно двічі: основна сесія й сесія для TC-10):

```bash
python save_auth.py chromium
```

**Крок 2. Запусти всі тести по черзі** (три етапи, кожен дає окремий HTML-звіт):

```bash
python run_all.py
```

| Етап | Що запускається | Фільтр |
|---|---|---|
| `main` | реєстрація, пошук, піни, дошки | `not tc07 and not tc08 and not tc10` |
| `logout` | TC-10 (вихід із системи) | `tc10` |
| `login` | TC-07, TC-08 (автоматичний вхід) | `tc07 or tc08` |

**Крок 3. Перед наступним повним прогоном** онови сесію для виходу (TC-10 її завершує):

```bash
python save_auth.py chromium logout
```

Якщо тести пишуть «Немає живої сесії», повтори крок 1.

### Корисні варіанти

| Мета | Команда |
|---|---|
| Без автоматичних входів | `python run_all.py --stages main,logout` |
| Лише основний етап | `python run_all.py --stages main` |
| Лише входи, окремо | `python run_all.py --stages login` |
| WebKit (рушій Safari) | `python save_auth.py webkit`, потім `python run_all.py --browser webkit` |
| Без вікна браузера | `python run_all.py --headless` |
| Не відкривати звіт | `python run_all.py --no-open` |
| Лише smoke-набір | `pytest -m smoke --headed` |
| Один файл | `pytest tests/test_search.py --headed` |
| Один тест | `pytest tests/test_search.py -k tc12 --headed` |
| Усі тести одним запуском з HTML | `pytest --html=reports/report.html --self-contained-html` |

HTML-звіти: `reports/*.html` (кожен файл самодостатній, відкривається подвійним кліком).

---

## 5. Відповідність тест-кейсів і автотестів

| Тест-кейс | Вимога | Автотест | Тип |
|---|---|---|---|
| TC-01, 02 | FR-1, FR-2 | Реєстрація (інтерактивні кроки) | ручний |
| TC-03 | FR-3 | `test_auth.py::test_tc03_signup_rejects_invalid_email_format` (4 набори даних) | авто |
| TC-04 | FR-4 | `test_auth.py::test_tc04_signup_password_rules` (3 набори) | авто |
| TC-05 | FR-5 | `test_auth.py::test_tc05_password_strength_indicator_is_shown` | авто |
| TC-06 | FR-6 | Підтвердження пошти | ручний |
| TC-07 | FR-7 | `test_auth.py::test_tc07_login_with_valid_credentials` | авто |
| TC-08 | FR-8 | `test_auth.py::test_tc08_login_with_wrong_password` | авто |
| TC-09 | FR-8 | Відновлення пароля | ручний |
| TC-10 | FR-9 | `test_auth.py::test_tc10_logout` | авто |
| TC-11 | FR-10 | `test_search.py::test_tc11_search_field_is_available_on_pages` (3 набори) | авто |
| TC-12 | FR-11 | `test_search.py::test_tc12_search_by_relevant_query` | авто |
| TC-13 | FR-12 | `test_search.py::test_tc13_autocomplete_suggestions` | авто |
| TC-14 | FR-13 | Фільтри пошуку | ручний |
| TC-15 | FR-14 | `test_search.py::test_tc15_search_without_results_shows_not_found_message` (+ `test_tc15b_*`) | авто, `xfail` |
| TC-16, 17 | FR-15, 16 | Перегляд піна, дії | ручний |
| TC-18 | FR-17 | `test_pins_boards.py::test_tc18_create_new_pin` | авто |
| TC-19 | FR-18 | `test_pins_boards.py::test_tc19_repin_existing_pin` | авто |
| TC-20 | FR-19 | `test_pins_boards.py::test_tc20_create_public_board` | авто |
| TC-21 | FR-20 | `test_pins_boards.py::test_tc21_create_secret_board` | авто |

Усього зібрано 22 автотести (з урахуванням параметризації). Ручні кейси виконуються за кроками з розділу 4 звіту.

---

## 6. Результати та відомі обмеження

- **TC-15 (xfail).** Для безглуздого запиту Pinterest показує схожі піни, а не «нічого не знайдено», як сказано в SRS. Це розбіжність специфікації з реальною поведінкою, зафіксована як очікувана невдача.
- **Реальна поведінка сайту відрізняється від SRS:** складність пароля (від 8 символів, а не 6), обов'язкове поле «Дата народження», перемикач «Make this board private» замість «secret».
- **TC-07, TC-08, TC-10 і CAPTCHA.** Повторні автоматичні входи Pinterest блокує перевіркою безпеки. Це реалізація ризику «CAPTCHA / блокування акаунта» з тест-плану. Тому входи винесено в окремі етапи, а TC-10 використовує окрему сесію.
- **Мова інтерфейсу.** Локатори написано під англійський інтерфейс (`locale: en-US` у контексті браузера).
- **Нестабільні локатори.** Pinterest часто змінює розмітку. Якщо тест падає на локаторі, зніми дамп сторінки та оновлюй відповідний Page Object (поля форми піна: `Title`, `Description`, `Link`, кнопка `Board`, `Publish`).

---

## 7. Ризики та ролі 

| Ризик | Ймовірність | Реакція |
|---|---|---|
| CAPTCHA / блокування під час входу | висока | збережені сесії, окремі етапи, ручне повторне збереження |
| Зміна розмітки сайту | середня | централізовані локатори в Page Object |
| Обмеження частоти запитів | середня | паузи між етапами, один тестовий акаунт |
| Нестабільність мережі | низька | таймаути в `.env`, повторний запуск |

Ролі: тест-аналітик і розробник автотестів (Величко Д. С.), рецензент (викладач).
