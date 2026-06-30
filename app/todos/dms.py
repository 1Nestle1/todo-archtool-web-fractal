"""Исходящие модели todos."""
import uuid
from datetime import datetime

from web_fractal.dtos import Base


class TodoDM(Base):
    id: uuid.UUID
    title: str
    is_done: bool
    user_id: uuid.UUID
    color: str
    group: str
    created_at: datetime
    updated_at: datetime
