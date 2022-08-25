import inspect
from typing import Optional

import dj_database_url
from pydantic import BaseSettings, SecretBytes, SecretStr, validator
from pydantic.fields import ModelField


class BaseDBConfig(BaseSettings):
    @validator("*")
    def format_config_from_dsn(cls, value: Optional[str], field: ModelField):
        if value is None:
            return {}

        if not isinstance(value, str):
            return value

        kwargs = {}
        conn_max_age: int = field.field_info.extra.get("conn_max_age", None)
        ssl_require: bool = field.field_info.extra.get('ssl_require', None)
        if conn_max_age is not None:
            kwargs['conn_max_age'] = conn_max_age
        if ssl_require is not None:
            kwargs['ssl_require'] = ssl_require
        return dj_database_url.parse(value, **kwargs)


def to_django(settings: BaseSettings):
    stack = inspect.stack()
    parent_frame = stack[1][0]
    for key, value in settings:
        if isinstance(value, BaseSettings):
            # for DATABASES and other complicated objects
            parent_frame.f_locals[key] = value.dict()
        elif isinstance(value, SecretStr) or isinstance(value, SecretBytes):
            parent_frame.f_locals[key] = value.get_secret_value()
        else:
            parent_frame.f_locals[key] = value
