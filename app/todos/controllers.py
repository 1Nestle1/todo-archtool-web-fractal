"""HTTP-контроллер todos."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.users.exceptions import UserNotFound

from .dms import TodoDM
from .dtos import CreateTodoDTO
from .exceptions import TodoNotFound
from .interfaces import TodoControllerABC, TodoServiceABC


class TodoController(TodoControllerABC):
    router = APIRouter(prefix="/todos", tags=["todos"])

    todo_service: TodoServiceABC

    def init_http_routes(self) -> None:
        self.reg_route(self.create_todo, methods=["POST"], path="/")
        self.reg_route(self.list_todos, methods=["GET"], path="/")
        self.reg_route(self.complete_todo, methods=["PATCH"], path="/{todo_id}/complete")

    async def create_todo(self, payload: CreateTodoDTO) -> TodoDM:
        try:
            return await self.todo_service.create_todo(payload)
        except UserNotFound as exc:
            # Нельзя создать задачу для несуществующего пользователя.
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc

    async def list_todos(self, user_id: UUID) -> list[TodoDM]:
        # user_id не в path → FastAPI трактует его как query-параметр: /todos/?user_id=...
        return await self.todo_service.list_todos(user_id)

    async def complete_todo(self, todo_id: UUID) -> TodoDM:
        try:
            return await self.todo_service.complete(todo_id)
        except TodoNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
