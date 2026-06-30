"""Контракты домена todos."""
from abc import abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from archtool.layers.default_layer_interfaces import (
    ABCController,
    ABCRepo,
    ABCService,
)
from web_fractal.http.interfaces import HttpControllerABC

from .dtos import CreateTodoDTO
from .dms import TodoDM

if TYPE_CHECKING:
    from .models import TodoORM


# ── Infrastructure ────────────────────────────────────────────────────────────
class TodoRepoABC(ABCRepo):
    """Доступ к данным задач."""

    @abstractmethod
    async def create(
        self, title: str, user_id: UUID, color: str, group: str
    ) -> "TodoORM":
        ...

    @abstractmethod
    async def list_for_user(self, user_id: UUID) -> list["TodoORM"]:
        ...

    @abstractmethod
    async def mark_done(self, todo_id: UUID) -> "TodoORM":
        """Помечает задачу выполненной. Бросает TodoNotFound, если нет."""
        ...


# ── Domain ────────────────────────────────────────────────────────────────────
class TodoServiceABC(ABCService):
    """Бизнес-логика задач."""

    @abstractmethod
    async def create_todo(self, payload: CreateTodoDTO) -> TodoDM:
        ...

    @abstractmethod
    async def list_todos(self, user_id: UUID) -> list[TodoDM]:
        ...

    @abstractmethod
    async def complete(self, todo_id: UUID) -> TodoDM:
        ...


# ── Application ───────────────────────────────────────────────────────────────
class TodoControllerABC(ABCController, HttpControllerABC):
    """HTTP API задач."""

    @abstractmethod
    async def create_todo(self, payload: CreateTodoDTO) -> TodoDM:
        ...

    @abstractmethod
    async def list_todos(self, user_id: UUID) -> list[TodoDM]:
        ...

    @abstractmethod
    async def complete_todo(self, todo_id: UUID) -> TodoDM:
        ...
