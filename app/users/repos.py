"""Реализация репозитория users. Сессией управляет web_fractal UnitOfWork,
открытый внутри метода через инъектированный `session_maker`.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from web_fractal.db import UnitOfWork, apply_filters

from .exceptions import UserAlreadyExists, UserNotFound
from .interfaces import UserRepoABC
from .models import UserORM


class UserRepo(UserRepoABC):
    # Зависимость объявлена аннотацией: archtool заинжектит зарегистрированный
    # session_maker (никаких __init__-параметров).
    session_maker: async_sessionmaker

    async def create(self, email: str, name: str) -> UserORM:
        async with UnitOfWork(self.session_maker) as uow:
            user = UserORM(email=email, name=name)
            await uow.register([user])  # add в сессию; commit — на выходе из UoW
            try:
                await uow.commit(refresh=True)  # flush+commit, затем refresh
            except IntegrityError as exc:
                await uow.rollback()
                raise UserAlreadyExists(email) from exc
            return user

    async def get(self, user_id: UUID) -> UserORM:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            stmt = apply_filters(select(UserORM), UserORM, {"id": user_id})
            user = (await session.execute(stmt)).scalars().first()
            if user is None:
                raise UserNotFound(user_id)
            return user
