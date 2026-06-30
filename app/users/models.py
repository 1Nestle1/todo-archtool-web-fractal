"""ORM-модель User. Наследует web_fractal `Base` (+ миксин `Dated` с created_at/updated_at)."""
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from web_fractal.db import Base, Dated


class UserORM(Base, Dated):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
