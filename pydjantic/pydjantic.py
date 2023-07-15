import inspect
from typing import Any, Optional

import dj_database_url
from pydantic import SecretBytes, SecretStr, validator, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.v1.fields import Field


class BaseDBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    @field_validator("*")
    def format_config_from_dsn(cls, value: Optional[str], info: FieldValidationInfo):
        if value is None:
            return {}

        if not isinstance(value, str):
            return value

        kwargs = {}
        # dj_database_url.parse does not accept **kwargs, so we can't blindly feed it with everything
        # https://github.com/jazzband/dj-database-url/blob/master/dj_database_url.py#L79
        known_dj_database_url_kwargs = [
            "engine",
            "conn_max_age",
            "conn_health_checks",
            "ssl_require",
            "test_options",
        ]
        for kwarg in known_dj_database_url_kwargs:
            json_schema_extra = (
                cls.model_fields[info.field_name].json_schema_extra or {}
            )
            field_extra = json_schema_extra.get(kwarg)
            if field_extra is not None:
                kwargs[kwarg] = field_extra
        return dj_database_url.parse(value, **kwargs)


def to_django(settings: BaseSettings):
    stack = inspect.stack()
    parent_frame = stack[1][0]

    def _get_actual_value(val: Any):
        if isinstance(val, BaseSettings):
            # for DATABASES and other complicated objects
            return _get_actual_value(val.model_dump())
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
