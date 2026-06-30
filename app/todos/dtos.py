"""Входящие модели todos."""
import uuid

from web_fractal.dtos import Base


class CreateTodoDTO(Base):
    """POST /todos/

    color и group необязательны — если их не передать, применятся дефолты
    ("slate" и "Inbox"). Базовый контракт остаётся {title, user_id}.
    """
    title: str
    user_id: uuid.UUID
    color: str | None = None
    group: str | None = None
