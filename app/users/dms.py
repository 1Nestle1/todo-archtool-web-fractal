"""Исходящие модели (то, что отдаём наружу). `from_attributes=True` в Base
позволяет собирать DM прямо из ORM-объекта через web_fractal `serialize`.
"""
import uuid
from datetime import datetime

from web_fractal.dtos import Base


class UserDM(Base):
    """Ответ с данными пользователя."""
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
