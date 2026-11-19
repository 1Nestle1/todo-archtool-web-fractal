# ToDo Service — archtool + web_fractal + FastAPI + SQLAlchemy (async)

Мини-проект, подтверждающий практическое понимание стека **archtool** (DI и контроль слоёв)
и **web_fractal** (батарейки поверх FastAPI + SQLAlchemy async).

Два ограниченных контекста (bounded contexts): **users** и **todos**. Все зависимости
объявлены аннотациями на конкретных классах, слои Clean Architecture проверяются до старта,
а к API приложена современная веб-страница с **реальным ToDo-листом** (цветные метки, списки,
отметка о выполнении) на странице `/todo`.

```
HTTP ──▶ Controller (Application) ──▶ Service (Domain) ──▶ Repo (Infrastructure) ──▶ DB
                                          │
                                          └─▶ UserService (cross-module, тот же слой Domain)
```

---

## Списки, метки и завершение задач

Откройте `/todo` и создайте пользователя. Добавьте задачу в список **Work**, выберите цвет и отметьте задачу выполненной. Фильтры **Active** и **Done** меняют выборку, а счётчики показывают результат по каждому списку. На снимке интерфейс отображает четыре демонстрационные задачи, одна уже выполнена.

![Четыре задачи в списках Work и Personal с метками, фильтрами и счётчиками](docs/images/feature.png)

## Стек

| Слой | Технология |
|------|-----------|
| DI / слои | archtool 2.1 |
| Веб-батарейки | web_fractal 0.0.1 (UnitOfWork, serialize, apply_filters, HttpControllerABC, ...) |
| HTTP | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| БД | SQLite (по умолчанию) или PostgreSQL |
| Схемы | Pydantic v2 |

---

## Структура проекта

```
todo_app/
├── entrypoints/
│   └── run.py                  # создание FastAPI + bundle(), запуск uvicorn
├── app/
│   ├── config.py               # DATABASE_URL, HOST, PORT
│   ├── archtool_conf/
│   │   ├── custom_layers.py    # APPS (модули) + app_layers (4 дефолтных слоя)
│   │   └── bundle_project.py   # bundle(): DI-инъекция + регистрация роутов
│   ├── users/                  # bounded context «пользователи»
│   │   ├── interfaces.py       # UserRepoABC, UserServiceABC, UserControllerABC
│   │   ├── exceptions.py       # UserNotFound, UserAlreadyExists
│   │   ├── dtos.py             # CreateUserDTO (вход)
│   │   ├── dms.py              # UserDM (выход)
│   │   ├── models.py           # UserORM
│   │   ├── repos.py            # UserRepo (UnitOfWork)
│   │   ├── services.py         # UserService
│   │   └── controllers.py      # UserController (FastAPI router)
│   └── todos/                  # bounded context «задачи»
│       ├── interfaces.py       # TodoRepoABC, TodoServiceABC, TodoControllerABC
│       ├── exceptions.py       # TodoNotFound
│       ├── dtos.py             # CreateTodoDTO
│       ├── dms.py              # TodoDM
│       ├── models.py           # TodoORM (FK на users.id)
│       ├── repos.py            # TodoRepo (UnitOfWork)
│       ├── services.py         # TodoService  ←  зависит от UserServiceABC!
│       └── controllers.py      # TodoController
├── web/
│   ├── index.html              # лендинг
│   └── todo.html               # сам ToDo-лист (страница /todo)
├── requirements.txt
└── pyproject.toml
```

---

## Запуск

Требуется **Python 3.11+** (проверено на 3.13).

```bash
# 1. перейти в каталог проекта
cd todo_app

# 2. виртуальное окружение
python -m venv .venv
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   Linux / macOS:
source .venv/bin/activate

# 3. зависимости
pip install -r requirements.txt

# 4. запуск (БД создаётся автоматически при старте)
uvicorn entrypoints.run:app --reload
```

Открыть в браузере:

| URL | Что это |
|-----|---------|
| http://127.0.0.1:8000/ | лендинг с кнопкой **Try ToDo list** |
| http://127.0.0.1:8000/todo | рабочий ToDo-лист (цвета, списки, отметки) |
| http://127.0.0.1:8000/docs | Swagger UI |

> **Порт.** По умолчанию 8000. Если он занят: `uvicorn entrypoints.run:app --port 8001`.

### База данных

Отдельный шаг создания БД не нужен: при старте в `lifespan` вызывается
`import_all_models()` и `Base.metadata.create_all()`, который создаёт файл `todo.db` (SQLite)
со всеми таблицами.

Чтобы использовать **PostgreSQL**, задайте DSN до запуска (БД должна существовать):

```bash
# Linux / macOS
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/todo"
# Windows PowerShell
$env:DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/todo"
pip install asyncpg
uvicorn entrypoints.run:app
```

---

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST  | `/users/` | Создать пользователя (`email`, `name`) |
| GET   | `/users/{id}` | Получить пользователя по ID |
| POST  | `/todos/` | Создать задачу (`title`, `user_id`, опц. `color`, `group`) |
| GET   | `/todos/?user_id=...` | Список задач пользователя |
| PATCH | `/todos/{id}/complete` | Отметить задачу выполненной |

> Поля `color` и `group` необязательны: если их не передать, применятся дефолты
> (`slate` и `Inbox`), поэтому базовый контракт `{title, user_id}` сохраняется.

---

## Примеры curl

```bash
# 1) создать пользователя
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@todo.svc","name":"Ada Lovelace"}'
```
```json
{ "id":"f7e69ba4-...", "email":"ada@todo.svc", "name":"Ada Lovelace",
  "created_at":"2026-06-30T14:48:42", "updated_at":"2026-06-30T14:48:42" }
```

```bash
# 2) получить пользователя
curl http://127.0.0.1:8000/users/f7e69ba4-...

# 3) создать задачу с цветом и списком
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Write Note G","user_id":"f7e69ba4-...","color":"sky","group":"Work"}'
```
```json
{ "id":"94efe905-...", "title":"Write Note G", "is_done":false,
  "user_id":"f7e69ba4-...", "color":"sky", "group":"Work",
  "created_at":"...", "updated_at":"..." }
```

```bash
# 4) список задач пользователя
curl "http://127.0.0.1:8000/todos/?user_id=f7e69ba4-..."

# 5) отметить выполненной
curl -X PATCH http://127.0.0.1:8000/todos/94efe905-.../complete
```

Проверка ошибок и кросс-модульной зависимости:

```bash
# несуществующий пользователь -> 404
curl -i http://127.0.0.1:8000/users/00000000-0000-0000-0000-000000000000

# дубль email -> 409
curl -i -X POST http://127.0.0.1:8000/users/ -H "Content-Type: application/json" \
  -d '{"email":"ada@todo.svc","name":"Dup"}'

# задача для несуществующего пользователя -> 404
# (TodoService.create_todo через UserService.ensure_exists проверяет владельца)
curl -i -X POST http://127.0.0.1:8000/todos/ -H "Content-Type: application/json" \
  -d '{"title":"orphan","user_id":"00000000-0000-0000-0000-000000000000"}'
```

---

## Как выполнены обязательные пункты

| Требование | Где |
|-----------|-----|
| `DependencyInjector` с передачей `layers` (все 4 дефолтных слоя) | [`bundle_project.py`](app/archtool_conf/bundle_project.py) (`build_injector`) + [`custom_layers.py`](app/archtool_conf/custom_layers.py) (`app_layers`) |
| Зависимости через аннотации на классах, без параметров `__init__` | все `repos.py` / `services.py` / `controllers.py` |
| `TodoService` зависит от `UserServiceABC` (кросс-модульно) | [`app/todos/services.py`](app/todos/services.py) |
| Репозитории используют `UnitOfWork` из web_fractal | [`app/users/repos.py`](app/users/repos.py), [`app/todos/repos.py`](app/todos/repos.py) |
| `session_maker` зарегистрирован через `injector.register()` | [`bundle_project.py`](app/archtool_conf/bundle_project.py) |
| Контроллеры наследуют `HttpControllerABC`, роуты в `init_http_routes()` | [`app/users/controllers.py`](app/users/controllers.py), [`app/todos/controllers.py`](app/todos/controllers.py) |
| `import_all_models()` и `initialize_controllers_api()` | [`bundle_project.py`](app/archtool_conf/bundle_project.py) |
| Запуск через `uvicorn`, все эндпоинты отвечают | [`entrypoints/run.py`](entrypoints/run.py) |
| Нет нарушений слоёв | `enforce_layers=True`; сервисы/репо не импортируют контроллеры |

### Как работает DI (кратко)

archtool сканирует каждый модуль из `APPS`: находит абстрактные контракты в `interfaces.py`
(наследники `ABCRepo` / `ABCService` / `ABCController`) и их единственные конкретные реализации
в `repos.py` / `services.py` / `controllers.py`. Классы инстанцируются **без аргументов**,
а зависимости подставляются во втором проходе по классовым аннотациям. Граф проверяется на
нарушение слоёв ещё до `inject()`.

`session_maker` нельзя «найти» сканированием (это async-ресурс), поэтому он регистрируется
вручную: `injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)`,
а репозитории получают его обычной аннотацией `session_maker: async_sessionmaker`.

---

## Замечание про зависимости

Пакет `web_fractal==0.0.1` не объявляет свои рантайм-зависимости в метаданных,
поэтому они явно зафиксированы в [`requirements.txt`](requirements.txt)
(`fastapi`, `sqlalchemy`, `pydantic`, `furl`, `pytz`, `aiohttp`, ...). Также `web_fractal 0.0.1`
обращается к контейнеру archtool через `injector._dependencies`, а archtool 2.x хранит его в
`injector.dependencies` — в `build_injector()` это согласовано одним алиасом (см. комментарий
в коде).
```
