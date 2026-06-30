"""Реализация репозитория todos. Использует web_fractal UnitOfWork."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from web_fractal.db import UnitOfWork, apply_filters

from .exceptions import TodoNotFound
from .interfaces import TodoRepoABC
from .models import TodoORM


class TodoRepo(TodoRepoABC):
    session_maker: async_sessionmaker

    async def create(
        self, title: str, user_id: UUID, color: str, group: str
    ) -> TodoORM:
        async with UnitOfWork(self.session_maker) as uow:
            todo = TodoORM(title=title, user_id=user_id, color=color, group=group)
            await uow.register([todo])
            await uow.commit(refresh=True)
            return todo

    async def list_for_user(self, user_id: UUID) -> list[TodoORM]:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            stmt = apply_filters(select(TodoORM), TodoORM, {"user_id": user_id})
            return list((await session.execute(stmt)).scalars().all())

    async def mark_done(self, todo_id: UUID) -> TodoORM:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            todo = await session.get(TodoORM, todo_id)
            if todo is None:
                raise TodoNotFound(todo_id)
            todo.is_done = True
            await uow.commit(refresh=True)
            return todo
