from typing import List

from pydantic import BaseSettings, Field, PostgresDsn

from pydjantic import BaseDBConfig, to_django


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
