"""
Django settings for demo project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from typing import Dict, List

from pydantic import Field
from pydantic.v1.fields import Undefined
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydjantic import BaseDBConfig, to_django

# Build paths inside the project like this: BASE_DIR / 'subdir'.
CUR_DIR = Path(__file__).resolve().parent
BASE_DIR = CUR_DIR.parent


class DatabaseSettings(BaseDBConfig):
    # https://docs.djangoproject.com/en/3.1/ref/settings/#databases
    default: str = Field(
        default=str(f"sqlite:///{BASE_DIR}/db.sqlite3"),
        validation_alias="DATABASE_URL",
        conn_max_age=0,
        ssl_require=False,
    )
    model_config = SettingsConfigDict(env_file=CUR_DIR / ".env")


class GeneralSettings(BaseSettings):
    # https://docs.djangoproject.com/en/dev/ref/settings/
    SECRET_KEY: str = Field(default=Undefined, validation_alias="DJANGO_SECRET_KEY")
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    DATABASES: DatabaseSettings = DatabaseSettings()

    ALLOWED_HOSTS: List[str] = []
    ROOT_URLCONF: str = "demo.urls"
    WSGI_APPLICATION: str = "demo.wsgi.application"

    INSTALLED_APPS: List[str] = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]

    MIDDLEWARE: List[str] = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    AUTH_PASSWORD_VALIDATORS: List[Dict] = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]


class I18NSettings(BaseSettings):
    # https://docs.djangoproject.com/en/3.1/topics/i18n/
    LANGUAGE_CODE: str = "en-us"
    TIME_ZONE: str = "UTC"
    USE_I18N: bool = True
    USE_L10N: bool = True
    USE_TZ: bool = True


class StaticSettings(BaseSettings):
    # https://docs.djangoproject.com/en/3.1/howto/static-files/
    STATIC_URL: str = "/static/"

    TEMPLATES: List[Dict] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]


class ProjectSettings(GeneralSettings, I18NSettings, StaticSettings):
    model_config = SettingsConfigDict(env_file=CUR_DIR / ".env")


to_django(ProjectSettings())
