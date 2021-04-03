import inspect
from typing import Optional

import dj_database_url
from pydantic import BaseSettings, validator


class BaseDBConfig(BaseSettings):
    @validator("*")
    def format_config_from_dsn(cls, value: Optional[str]):
        if value is None:
            return {}

        return dj_database_url.parse(value)


def to_django(settings: BaseSettings):
    stack = inspect.stack()
    parent_frame = stack[1][0]
    for key, value in settings:
        if isinstance(value, BaseSettings):
            # for DATABASES and other complicated objects
            parent_frame.f_locals[key] = value.dict()
        else:
            parent_frame.f_locals[key] = value
