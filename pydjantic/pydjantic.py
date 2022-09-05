import inspect
from typing import Any, Optional

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

    def _get_actual_value(val: Any):
        if isinstance(val, BaseSettings):
            # for DATABASES and other complicated objects
            return _get_actual_value(val.dict())
        elif isinstance(val, dict):
            return {k: _get_actual_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [_get_actual_value(item) for item in val]
        elif isinstance(val, SecretStr) or isinstance(val, SecretBytes):
            return val.get_secret_value()
        else:
            return val

    for key, value in settings:
        parent_frame.f_locals[key] = _get_actual_value(value)
