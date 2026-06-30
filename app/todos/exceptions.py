"""Доменные исключения todos."""
import uuid


class TodoError(Exception):
    """Базовое доменное исключение домена Todo."""


class TodoNotFound(TodoError):
    def __init__(self, todo_id: uuid.UUID):
        self.todo_id = todo_id
        super().__init__(f"Задача {todo_id} не найдена")
