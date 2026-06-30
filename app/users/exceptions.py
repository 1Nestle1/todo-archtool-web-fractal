"""Доменные исключения users. Без HTTP — маппинг в коды делает контроллер."""
import uuid


class UserError(Exception):
    """Базовое доменное исключение домена User."""


class UserNotFound(UserError):
    def __init__(self, user_id: uuid.UUID):
        self.user_id = user_id
        super().__init__(f"Пользователь {user_id} не найден")


class UserAlreadyExists(UserError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Пользователь с email={email} уже существует")
