from typing import Dict, Optional

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from tempenv import TemporaryEnvironment

from pydjantic import BaseDBConfig


def test_empty():
    class DatabaseConfig(BaseDBConfig):
        default: Optional[PostgresDsn] = None
        replica: Optional[Dict] = None

    db_settings = DatabaseConfig()
    assert db_settings.model_dump() == {"default": {}, "replica": {}}


def test_dsn():
    class DatabaseConfig(BaseDBConfig):
        default: str = Field(default="postgres://user:password@hostname:5432/dbname")

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "hostname",
        "NAME": "dbname",
        "PASSWORD": "password",
        "PORT": 5432,
        "USER": "user",
    }


def test_dsn_extra_params():
    class DatabaseConfig(BaseDBConfig):
        default: str = Field(
            default="postgres://user:password@hostname:5432/dbname?connect_timeout=10",
            json_schema_extra={
                "test_options": {"NAME": "mytestdb"},
                "engine": "my.custom.backend",
                "conn_health_checks": True,
                "ssl_require": "True",
                "conn_max_age": 60,
            },
        )

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "ENGINE": "my.custom.backend",
        "HOST": "hostname",
        "NAME": "dbname",
        "OPTIONS": {"connect_timeout": 10, "sslmode": "require"},
        "PASSWORD": "password",
        "PORT": 5432,
        "USER": "user",
        "TEST": {"NAME": "mytestdb"},
    }


class PostgresDB(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    ENGINE: str = "django.db.backends.postgresql"
    HOST: str = Field(default="replicahost")
    NAME: str = Field(default="replicadbname")
    PASSWORD: str = Field(default="replicapwd")
    PORT: int = Field(default=5432)
    USER: str = Field(default="replicauser")
    OPTIONS: dict = Field(default={})
    CONN_MAX_AGE: int = Field(default=0)
    CONN_HEALTH_CHECKS: bool = Field(default=False)


def test_exact():
    class DatabaseConfig(BaseSettings):
        default: PostgresDB = PostgresDB()

    db_settings = DatabaseConfig()
    assert db_settings.model_dump() == {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "replicahost",
            "NAME": "replicadbname",
            "USER": "replicauser",
            "PASSWORD": "replicapwd",
            "PORT": 5432,
            "OPTIONS": {},
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": False,
        }
    }


def test_dsn_and_exact_config():
    class DatabaseConfig(BaseDBConfig):
        default: str = Field(default="postgres://user:password@hostname:5432/dbname")
        replica: PostgresDB = PostgresDB()

    db_settings = DatabaseConfig()
    assert db_settings.model_dump() == {
        "default": {
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": False,
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "hostname",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 5432,
            "USER": "user",
        },
        "replica": {
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": False,
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "replicahost",
            "NAME": "replicadbname",
            "USER": "replicauser",
            "PASSWORD": "replicapwd",
            "OPTIONS": {},
            "PORT": 5432,
        },
    }


def test_env_vars_for_exact_config():
    with TemporaryEnvironment(
        {
            "DATABASE_CONN_MAX_AGE": "60",
            "DATABASE_OPTIONS": '{"sslmode": "require"}',
        }
    ):

        class DatabaseConfig(BaseSettings):
            default: PostgresDB = PostgresDB()

        db_settings = DatabaseConfig()
        assert db_settings.model_dump() == {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "replicahost",
                "NAME": "replicadbname",
                "USER": "replicauser",
                "PASSWORD": "replicapwd",
                "PORT": 5432,
                "OPTIONS": {"sslmode": "require"},
                "CONN_MAX_AGE": 60,
                "CONN_HEALTH_CHECKS": False,
            },
        }
