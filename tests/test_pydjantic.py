from typing import List, Optional

from pydantic import BaseSettings, Field, PostgresDsn

from pydjantic import BaseDBConfig, to_django


def test_empty_database_config():
    class DatabaseConfig(BaseDBConfig):
        default: Optional[PostgresDsn] = Field()

    db_settings = DatabaseConfig()
    assert db_settings.default == {}


def test_database_config():
    class DatabaseConfig(BaseDBConfig):
        default: PostgresDsn = Field(
            default="postgres://user:password@hostname:5432/database_name", env="DATABASE_URL"
        )

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        'CONN_MAX_AGE': 0,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'hostname',
        'NAME': 'database_name',
        'PASSWORD': 'password',
        'PORT': 5432,
        'USER': 'user',
    }


def test_conn_max_age_ssl_require():
    class DatabaseConfig(BaseDBConfig):
        default: PostgresDsn = Field(
            default="postgres://user:password@hostname:5432/database_name",
            env="DATABASE_URL",
            conn_max_age=60,
            ssl_require=True
        )

    db_settings = DatabaseConfig()
    assert db_settings.default == {
        'CONN_MAX_AGE': 60,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'hostname',
        'NAME': 'database_name',
        'OPTIONS': {'sslmode': 'require'},
        'PASSWORD': 'password',
        'PORT': 5432,
        'USER': 'user',
    }


def test_to_django_settings():
    class DatabaseConfig(BaseDBConfig):
        default: PostgresDsn = Field(
            default="postgres://user:password@hostname:5432/database_name", env="DATABASE_URL"
        )

    class GeneralSettings(BaseSettings):
        DEBUG: bool = Field(default=False, env='DEBUG')
        INSTALLED_APPS: List[str] = [
            'django.contrib.admin',
            'django.contrib.auth',
        ]
        LANGUAGE_CODE: str = 'en-us'
        USE_TZ: bool = True
        DATABASES: DatabaseConfig = DatabaseConfig()

    class StaticSettings(BaseSettings):
        STATIC_URL: str = '/static/'
        STATIC_ROOT: str = 'staticfiles'

    class ProjectSettings(GeneralSettings, StaticSettings):
        pass

    to_django(ProjectSettings())
    assert locals()['DEBUG'] is False
    assert locals()['INSTALLED_APPS'] == ['django.contrib.admin', 'django.contrib.auth']
    assert locals()['LANGUAGE_CODE'] == 'en-us'
    assert locals()['USE_TZ'] is True
    assert locals()['STATIC_URL'] == '/static/'
    assert locals()['STATIC_ROOT'] == 'staticfiles'
    assert locals()['DATABASES'] == {
        'default': {
            'CONN_MAX_AGE': 0,
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'hostname',
            'NAME': 'database_name',
            'PASSWORD': 'password',
            'PORT': 5432,
            'USER': 'user',
        }
    }
