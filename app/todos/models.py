"""ORM-модель Todo. FK на users.id связывает задачу с пользователем."""
import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from web_fractal.db import Base, Dated


class TodoORM(Base, Dated):
    __tablename__ = "todos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    # Опциональные поля для UI: цветовая метка и группа/список.
    # Дефолты применяются в сервисе, поэтому базовый контракт
    # (POST с одним title+user_id) продолжает работать.
    color: Mapped[str] = mapped_column(String(16), default="slate")
    group: Mapped[str] = mapped_column(String(64), default="Inbox", index=True)
