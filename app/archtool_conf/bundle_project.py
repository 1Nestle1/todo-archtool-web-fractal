"""Сборка приложения: DI-инъекция + FastAPI.

`bundle()` делает всё, что нужно для готового ASGI-приложения:
  1. создаёт async-engine и `session_maker`;
  2. строит `DependencyInjector` со всеми 4 слоями и регистрирует `session_maker`
     вручную через `injector.register()`;
  3. `injector.inject()` — двухпроходная инъекция с проверкой слоёв;
  4. `initialize_controllers_api()` — подключает роуты контроллеров к FastAPI;
  5. в lifespan через `import_all_models()` создаёт таблицы.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from archtool.dependency_injector import DependencyInjector
from web_fractal.db import Base

from app import config
from app.archtool_conf.custom_layers import APPS, app_layers

# Корень проекта (…/todo_app). Передаём явно в DependencyInjector,
# чтобы archtool не угадывал его и не трогал sys.path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_injector(session_maker: async_sessionmaker) -> DependencyInjector:
    """Собирает и заполняет DI-контейнер."""
    injector = DependencyInjector(
        modules_list=APPS,
        layers=app_layers,            # все 4 дефолтных слоя
        project_root=PROJECT_ROOT,
        enforce_layers=True,          # падать при нарушении слоёв ещё до старта
    )

    # web_fractal 0.0.1 читает контейнер через приватный атрибут `_dependencies`,
    # а archtool 2.x хранит его в публичном `dependencies`. Объекты-словарь один и тот же,
    # поэтому достаточно одного алиаса (никаких копий состояния).
    injector._dependencies = injector.dependencies

    # session_maker — async-ресурс, его нельзя «найти» сканированием.
    # Регистрируем готовый объект вручную; inject_into=False — это сторонний
    # объект SQLAlchemy без archtool-аннотаций.
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)

    # Pass 1 (discovery) → проверка слоёв → Pass 2 (setattr-инъекция).
    injector.inject()
    return injector


def bundle() -> FastAPI:
    """Точка сборки ASGI-приложения для uvicorn."""
    engine = create_async_engine(config.DATABASE_URL, echo=config.SQL_ECHO)
    session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    injector = build_injector(session_maker)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        # Импортируем все ORM-модели проекта (регистрируются на Base.metadata)
        # и создаём таблицы. Делаем это в lifespan — внутри event-loop uvicorn.
        from web_fractal.building_utils import import_all_models

        import_all_models(Base)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await engine.dispose()

    app = FastAPI(
        title="ToDo Service",
        version="1.0.0",
        description="archtool + web_fractal + FastAPI + SQLAlchemy (async)",
        lifespan=lifespan,
    )

    # Подключаем роутеры всех HttpControllerABC-контроллеров из контейнера.
    from web_fractal.building_utils import initialize_controllers_api

    initialize_controllers_api(injector, app)

    # Современная статичная landing-страница с живым демо API (тот же origin).
    from fastapi.responses import FileResponse

    web_dir = PROJECT_ROOT / "web"

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/todo", include_in_schema=False)
    async def todo_app_page() -> FileResponse:
        return FileResponse(web_dir / "todo.html")

    # Держим ссылки, чтобы их не собрал GC и можно было достать в тестах.
    app.state.injector = injector
    app.state.engine = engine
    return app
