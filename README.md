# pydjantic
[![Build Status](https://github.com/ErhoSen/pydjantic/actions/workflows/main.yml/badge.svg)](https://github.com/ErhoSen/pydjantic/actions)
[![codecov](https://codecov.io/gh/ErhoSen/pydjantic/branch/master/graph/badge.svg?token=BW5A0V3CR3)](https://codecov.io/gh/ErhoSen/pydjantic)
[![pypi](https://img.shields.io/pypi/v/pydjantic.svg)](https://pypi.org/project/pydjantic/)
[![versions](https://img.shields.io/pypi/pyversions/pydjantic.svg)](https://github.com/ErhoSen/pydjantic)
[![license](https://img.shields.io/github/license/erhosen/pydjantic.svg)](https://github.com/ErhoSen/pydjantic/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Use Pydantic Settings in your Django application.

![Pydjantc django settings](https://github.com/ErhoSen/pydjantic/raw/master/images/pydjantic.png "Pydjantc django settings")

## Introduction

If you are tired of the mess in your Django Settings - I feel your pain:
* Ridiculously long `settings.py` file, with ASCII-art separation
* `from common import *` Python [anti-pattern](https://www.geeksforgeeks.org/why-import-star-in-python-is-a-bad-idea/)
* `try: <import> except: ImportError` Python [anti-pattern](https://stackoverflow.com/questions/14050281/how-to-check-if-a-python-module-exists-without-importing-it)
* `base.py`, `production.py`, `local.py`, `domain.py` - bunch of unrelated modules that override each other
* [django-environ](https://github.com/joke2k/django-environ) library, that do even worse...

On the other hand we have [Pydantic Settings](https://pydantic-docs.helpmanual.io/usage/settings/),
which is de-facto standard for all non-django projects.

If you love Pydantic settings management approach, **Pydjantic** is a right tool for you.

**Pydjantic** allows you to define your settings in familiar way - just inherit from `BaseSettings`:
```py
from typing import List

from pydantic import BaseSettings, Field
from pydantic.fields import Undefined
from pydjantic import to_django

class GeneralSettings(BaseSettings):
    SECRET_KEY: str = Field(default=Undefined, env='DJANGO_SECRET_KEY')
    DEBUG: bool = Field(default=False, env='DEBUG')
    INSTALLED_APPS: List[str] = [
        'django.contrib.admin',
        'django.contrib.auth',
    ]
    LANGUAGE_CODE: str = 'en-us'
    USE_TZ: bool = True


class StaticSettings(BaseSettings):
    STATIC_URL: str = '/static/'
    STATIC_ROOT: str = 'staticfiles'


class SentrySettings(BaseSettings):
    SENTRY_DSN: str = Field(default=Undefined, env='SENTRY_DSN')


class ProjectSettings(GeneralSettings, StaticSettings, SentrySettings):
    pass


to_django(ProjectSettings())
```
You can create as many classes/modules as you want, to achieve perfect settings' management.
Divide your settings by domains, and then create final `ProjectSettings` class, that inherits from these domains.

Provide the instance of `ProjectSettings` to `to_django` function.
That's all, your django settings will work as expected.

## Installation

Install using `pip install -U pydjantic` or `poetry add pydjantic`.

## Example
In the `/demo` directory you can find a [working Django app](https://github.com/ErhoSen/pydjantic/tree/master/demo) with [pydjantic settings](https://github.com/ErhoSen/pydjantic/blob/master/demo/demo/settings.py).

## Database configuration

**Pydjantic** comes with a special helper for managing DB configs - `BaseDBConfig`. See example below:
```py
from pydantic import Field, PostgresDsn
from pydjantic import BaseDBConfig


class DatabaseConfig(BaseDBConfig):
    default: PostgresDsn = Field(
        default="postgres://user:password@hostname:5432/database_name", env="DATABASE_URL",
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
```
Additionally, you can specify `conn_max_age` and `ssl_require` options.

They will be provided as-is to [dj-database-url](https://pypi.org/project/dj-database-url/) library, that handles the transformation from dsn to django format.
```python
class DatabaseConfig(BaseDBConfig):
    default: PostgresDsn = Field(default=Undefined, env="DATABASE_URL", conn_max_age=60, ssl_require=True)
```
