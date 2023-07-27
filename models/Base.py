from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Column, DateTime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func


# =======================================================

class Base(DeclarativeBase):
    pass
