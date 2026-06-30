"""Входящие модели (то, что приходит с фронта). Наследуют web_fractal Base (pydantic)."""
from pydantic import EmailStr

from web_fractal.dtos import Base


class CreateUserDTO(Base):
    """POST /users/"""
    email: EmailStr
    name: str
