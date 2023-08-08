import os
import re
from datetime import datetime, date

# import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr, declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


@as_declarative(metadata=metadata)
class Base:
    __table_args__ = {"mysql_engine": "InnoDB", "extend_existing": True}

    @declared_attr
    def __tablename__(cls):
        return re.sub("(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {
            field.name: getattr(self, field.name)
            if not isinstance(getattr(self, field.name), datetime)
            else str(getattr(self, field.name))
            for field in self.__table__.c
        }


async def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()