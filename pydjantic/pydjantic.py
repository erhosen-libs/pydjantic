import inspect
from typing import Optional

import dj_database_url
from pydantic import BaseSettings, validator
from pydantic.fields import ModelField


class BaseDBConfig(BaseSettings):
    @validator("*")
    def format_config_from_dsn(cls, value: Optional[str], field: ModelField):
        if value is None:
            return {}

        conn_max_age: int = field.field_info.extra.get("conn_max_age", 0)
        ssl_require: bool = field.field_info.extra.get('ssl_require', False)
        return dj_database_url.parse(value, conn_max_age=conn_max_age, ssl_require=ssl_require)


def to_django(settings: BaseSettings):
    stack = inspect.stack()
    parent_frame = stack[1][0]
    for key, value in settings:
        if isinstance(value, BaseSettings):
            # for DATABASES and other complicated objects
            parent_frame.f_locals[key] = value.dict()
        else:
            parent_frame.f_locals[key] = value
