from sqlalchemy.orm import DeclarativeBase
from enum import Enum


class Base(DeclarativeBase):
    pass


class Source(Enum):
    dex = "dex"
    cex = "cex"


class UserRole(Enum):
    admin = "admin"
    user = "user"
