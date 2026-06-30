"""HTTP-контроллер users. Единственное место, где доменные исключения
превращаются в HTTPException. Роуты регистрируются в init_http_routes().
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from .dms import UserDM
from .dtos import CreateUserDTO
from .exceptions import UserAlreadyExists, UserNotFound
from .interfaces import UserControllerABC, UserServiceABC


class UserController(UserControllerABC):
    # router — обычное поле (без аннотации), чтобы archtool не счёл его зависимостью.
    router = APIRouter(prefix="/users", tags=["users"])

    # Зависимость на сервис (слой Domain) — через аннотацию.
    user_service: UserServiceABC

    def init_http_routes(self) -> None:
        self.reg_route(self.create_user, methods=["POST"], path="/")
        self.reg_route(self.get_user, methods=["GET"], path="/{user_id}")

    async def create_user(self, payload: CreateUserDTO) -> UserDM:
        try:
            return await self.user_service.register(payload)
        except UserAlreadyExists as exc:
            raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    async def get_user(self, user_id: UUID) -> UserDM:
        try:
            return await self.user_service.get_user(user_id)
        except UserNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
