"""Бизнес-логика todos.

Здесь живёт КРОСС-МОДУЛЬНАЯ зависимость: TodoService зависит от UserServiceABC
(домен users) и проверяет существование пользователя перед созданием задачи.
Оба — слой Domain, поэтому нарушения слоёв нет.
"""
from uuid import UUID

from web_fractal.db import serialize

from app.users.interfaces import UserServiceABC

from .dms import TodoDM
from .dtos import CreateTodoDTO
from .interfaces import TodoRepoABC, TodoServiceABC


class TodoService(TodoServiceABC):
    # Зависимость на свой репозиторий (Infrastructure).
    todo_repo: TodoRepoABC
    # КРОСС-МОДУЛЬНАЯ зависимость на сервис чужого домена (Domain).
    user_service: UserServiceABC

    async def create_todo(self, payload: CreateTodoDTO) -> TodoDM:
        # Бросит UserNotFound, если пользователя нет — задачу не создаём.
        await self.user_service.ensure_exists(payload.user_id)
        # Применяем дефолты для необязательных UI-полей.
        color = payload.color or "slate"
        group = (payload.group or "Inbox").strip() or "Inbox"
        todo = await self.todo_repo.create(
            title=payload.title,
            user_id=payload.user_id,
            color=color,
            group=group,
        )
        return serialize(TodoDM, todo, as_list=False)

    async def list_todos(self, user_id: UUID) -> list[TodoDM]:
        todos = await self.todo_repo.list_for_user(user_id)
        return serialize(TodoDM, todos, as_list=True)

    async def complete(self, todo_id: UUID) -> TodoDM:
        todo = await self.todo_repo.mark_done(todo_id)
        return serialize(TodoDM, todo, as_list=False)
