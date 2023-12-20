import inspect
from typing import Any

import dj_database_url
from pydantic import SecretBytes, SecretStr, ValidationInfo, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseDBConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    @field_validator("*")
    def format_config_from_dsn(cls, value: Any, info: ValidationInfo):
        if value is None:
            return {}

        if not isinstance(value, (str, MultiHostUrl)):
            return value

        kwargs = {}
        # dj_database_url.parse does not accept **kwargs, so we can't blindly feed it with everything
        # https://github.com/jazzband/dj-database-url/blob/9292e1fa8af99a73e6c9cbdd7321236741016c06/dj_database_url/__init__.py#L79C8-L79C8
        known_dj_database_url_kwargs = [
            "engine",
            "conn_max_age",
            "conn_health_checks",
            "disable_server_side_cursors",
            "ssl_require",
            "test_options",
        ]

        if info.field_name:
            extra = cls.model_fields[info.field_name].json_schema_extra
            if isinstance(extra, dict):
                for kwarg in known_dj_database_url_kwargs:
                    field_extra = extra.get(kwarg)
                    if field_extra is not None:
                        kwargs[kwarg] = field_extra
        return dj_database_url.parse(str(value), **kwargs)


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

    for key, value in settings.model_dump().items():
        parent_frame.f_locals[key] = _get_actual_value(value)
