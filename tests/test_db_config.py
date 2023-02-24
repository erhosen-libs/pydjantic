from typing import Dict, Optional

from pydantic import BaseSettings, Field, PostgresDsn
from tempenv import TemporaryEnvironment

from pydjantic import BaseDBConfig


def test_empty():
    class DatabaseConfig(BaseDBConfig):
        default: Optional[PostgresDsn] = Field()
        replica: Optional[Dict] = Field()

    db_settings = DatabaseConfig()
    assert db_settings.dict() == {'default': {}, 'replica': {}}


def test_dsn():
    class DatabaseConfig(BaseDBConfig):
        default = Field(default="postgres://user:password@hostname:5432/dbname")

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'hostname',
        'NAME': 'dbname',
        'PASSWORD': 'password',
        'PORT': 5432,
        'USER': 'user',
    }


def test_dsn_extra_params():
    class DatabaseConfig(BaseDBConfig):
        default = Field(
            default="postgres://user:password@hostname:5432/dbname",
            conn_max_age=60,
            ssl_require=True,
            conn_health_checks=True,
            engine='my.custom.backend',
            test_options={'NAME': 'mytestdb'},
        )

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
        'ENGINE': 'my.custom.backend',
        'HOST': 'hostname',
        'NAME': 'dbname',
        'OPTIONS': {'sslmode': 'require'},
        'PASSWORD': 'password',
        'PORT': 5432,
        'USER': 'user',
        'TEST': {'NAME': 'mytestdb'}
    }


class PostgresDB(BaseSettings):
    ENGINE: str = 'django.db.backends.postgresql'
    HOST: str = Field(default='replicahost', env='DATABASE_HOST')
    NAME: str = Field(default='replicadbname', env='DATABASE_NAME')
    PASSWORD: str = Field(default='replicapwd', env='DATABASE_PASSWORD')
    PORT: int = Field(default=5432, env='DATABASE_PORT')
    USER: str = Field(default='replicauser', env='DATABASE_USER')
    OPTIONS: dict = Field(default={}, env='DATABASE_OPTIONS')
    CONN_MAX_AGE: int = Field(default=0, env='DATABASE_CONN_MAX_AGE')
    CONN_HEALTH_CHECKS: bool = Field(default=False, env="DATABASE_CONN_HEALTH_CHECKS")


def test_exact():
    class DatabaseConfig(BaseSettings):
        default = PostgresDB()

    db_settings = DatabaseConfig()
    assert db_settings.dict() == {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'replicahost',
            'NAME': 'replicadbname',
            'USER': 'replicauser',
            'PASSWORD': 'replicapwd',
            'PORT': 5432,
            'OPTIONS': {},
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False
        }
    }


def test_dsn_and_exact_config():
    class DatabaseConfig(BaseDBConfig):
        default = Field(default="postgres://user:password@hostname:5432/dbname")
        replica = PostgresDB()

    db_settings = DatabaseConfig()
    assert db_settings.dict() == {
        'default': {
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False,
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'hostname',
            'NAME': 'dbname',
            'PASSWORD': 'password',
            'PORT': 5432,
            'USER': 'user',
        },
        'replica': {
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False,
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'replicahost',
            'NAME': 'replicadbname',
            'USER': 'replicauser',
            'PASSWORD': 'replicapwd',
            'OPTIONS': {},
            'PORT': 5432,
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
            default = PostgresDB()

        db_settings = DatabaseConfig()
        assert db_settings.dict() == {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': 'replicahost',
                'NAME': 'replicadbname',
                'USER': 'replicauser',
                'PASSWORD': 'replicapwd',
                'PORT': 5432,
                'OPTIONS': {'sslmode': 'require'},
                'CONN_MAX_AGE': 60,
                'CONN_HEALTH_CHECKS': False
            },
        }
