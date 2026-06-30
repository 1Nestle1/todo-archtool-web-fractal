"""Точка входа: создаёт FastAPI-приложение через bundle().

Запуск:
    uvicorn entrypoints.run:app --reload      # из каталога todo_app/
или:
    python -m entrypoints.run                 # поднимет uvicorn сам
"""
import os
import sys
import warnings
from pathlib import Path

# web_fractal 0.0.1 объявляет pydantic-конфиг со старым ключом
# (`allow_population_by_field_name`). Глушим только этот шумный дефолт-варнинг.
warnings.filterwarnings(
    "ignore", message="Valid config keys have changed in V2", category=UserWarning
)

# Корень проекта (…/todo_app). Делаем его текущим каталогом и кладём в sys.path,
# чтобы пакеты `app`/`entrypoints` импортировались, а относительные пути
# web_fractal.import_all_models («./app/<module>/models.py») разрешались.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.archtool_conf.bundle_project import bundle  # noqa: E402

# ASGI-объект, который ищет uvicorn по строке "entrypoints.run:app".
app = bundle()


if __name__ == "__main__":
    import uvicorn

    from app import config

    uvicorn.run("entrypoints.run:app", host=config.HOST, port=config.PORT, reload=False)
