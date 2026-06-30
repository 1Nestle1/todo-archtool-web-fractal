"""Бизнес-логика users. Оркестрирует репозиторий и сериализует ORM → DM."""
from uuid import UUID

from web_fractal.db import serialize

from .dms import UserDM
from .dtos import CreateUserDTO
from .interfaces import UserRepoABC, UserServiceABC


class UserService(UserServiceABC):
    # Зависимость на репозиторий (внутренний слой Infrastructure) — через аннотацию.
    user_repo: UserRepoABC

    async def register(self, payload: CreateUserDTO) -> UserDM:
        user = await self.user_repo.create(email=payload.email, name=payload.name)
        return serialize(UserDM, user, as_list=False)

    async def get_user(self, user_id: UUID) -> UserDM:
        user = await self.user_repo.get(user_id)
        return serialize(UserDM, user, as_list=False)

    async def ensure_exists(self, user_id: UUID) -> None:
        # Бросит UserNotFound, если пользователя нет. Используется доменом todos.
        await self.user_repo.get(user_id)
