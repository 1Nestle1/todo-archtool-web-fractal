"""Контракты домена users. Только абстракции — archtool находит реализации
по имени файла (repos/services/controllers) и суперклассу.
"""
from abc import abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from archtool.layers.default_layer_interfaces import (
    ABCController,
    ABCRepo,
    ABCService,
)
from web_fractal.http.interfaces import HttpControllerABC

from .dtos import CreateUserDTO
from .dms import UserDM

if TYPE_CHECKING:
    from .models import UserORM


# ── Infrastructure ────────────────────────────────────────────────────────────
class UserRepoABC(ABCRepo):
    """Доступ к данным пользователей."""

    @abstractmethod
    async def create(self, email: str, name: str) -> "UserORM":
        """Создаёт пользователя. Бросает UserAlreadyExists при дубле email."""
        ...

    @abstractmethod
    async def get(self, user_id: UUID) -> "UserORM":
        """Возвращает пользователя по id. Бросает UserNotFound, если нет."""
        ...


# ── Domain ────────────────────────────────────────────────────────────────────
class UserServiceABC(ABCService):
    """Бизнес-логика пользователей."""

    @abstractmethod
    async def register(self, payload: CreateUserDTO) -> UserDM:
        ...

    @abstractmethod
    async def get_user(self, user_id: UUID) -> UserDM:
        ...

    @abstractmethod
    async def ensure_exists(self, user_id: UUID) -> None:
        """Проверяет, что пользователь существует (для кросс-модульных вызовов)."""
        ...


# ── Application ───────────────────────────────────────────────────────────────
class UserControllerABC(ABCController, HttpControllerABC):
    """HTTP API пользователей."""

    @abstractmethod
    async def create_user(self, payload: CreateUserDTO) -> UserDM:
        ...

    @abstractmethod
    async def get_user(self, user_id: UUID) -> UserDM:
        ...
