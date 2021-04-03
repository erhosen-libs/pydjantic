# pydjantic
[![Build Status](https://github.com/ErhoSen/pydjantic/actions/workflows/main.yml/badge.svg)](https://github.com/ErhoSen/pydjantic/actions)
[![codecov](https://codecov.io/gh/ErhoSen/pydjantic/branch/master/graph/badge.svg?token=BW5A0V3CR3)](https://codecov.io/gh/ErhoSen/pydjantic)
[![pypi](https://img.shields.io/pypi/v/pydjantic.svg)](https://pypi.org/project/pydjantic/)
[![versions](https://img.shields.io/pypi/pyversions/pydjantic.svg)](https://github.com/ErhoSen/pydjantic)
[![license](https://img.shields.io/github/license/erhosen/pydjantic.svg)](https://github.com/ErhoSen/pydjantic/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Use Pydantic Settings for your Django app.

## Introduction

If you are tired of the mess in your Django Settings - I feel your pain:
* Long as Dostoevsky's "Crime and punishment" `settings.py` file
* `from production import *` anti-pattern
* `try: <import> except: ImportError` anti-pattern
* `base.py`, `production.py`, `local.py`, `domain.py` - bunch of modules that override each other
* [django-environ](https://github.com/joke2k/django-environ) library, that did even worse...

**Pydjantic** offers to divide the settings only by their domain:
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
You can create as many classes/modules as you want, to achieve perfect settings management.

Just create final `ProjectSettings` class, that inherits from these domains, and provide its instance to `to_django` function.
That's all, your django settings will work as expected.

## Installation

Install using `pip install -U pydantic` or `poetry add pydjantic`.
