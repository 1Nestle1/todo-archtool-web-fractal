"""Конфигурация приложения.

web_fractal читает значения отсюда через `get_settings_value(s)` —
функции делают `from app import config as settings` и берут атрибуты по имени.
Поэтому все настройки объявлены модульного уровня.
"""
import os

# Async-DSN для SQLAlchemy. По умолчанию — локальный SQLite (aiosqlite),
# чтобы проект поднимался без внешней БД. Можно переопределить переменной окружения,
# например: postgresql+asyncpg://user:pass@localhost:5432/todo
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./todo.db")

# Параметры HTTP-сервера (uvicorn).
HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "8000"))

# Печатать ли SQL в лог.
SQL_ECHO: bool = os.getenv("SQL_ECHO", "0") == "1"
