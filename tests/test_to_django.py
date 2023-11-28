from typing import Any, Dict, List

from deepdiff import DeepDiff
from pydantic import Field, PostgresDsn, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings

from pydjantic import BaseDBConfig, to_django


def test_to_django_settings():
    class DatabaseConfig(BaseDBConfig):
        default: PostgresDsn = Field(
            default="postgres://user:password@hostname:5432/dbname",
            validation_alias="DATABASE_URL",
        )

    class GeneralSettings(BaseSettings):
        DEBUG: bool = Field(default=False)
        INSTALLED_APPS: List[str] = [
            "django.contrib.admin",
            "django.contrib.auth",
        ]
        LANGUAGE_CODE: str = "en-us"
        USE_TZ: bool = True
        DATABASES: DatabaseConfig = DatabaseConfig()

    class StaticSettings(BaseSettings):
        STATIC_URL: str = "/static/"
        STATIC_ROOT: str = "staticfiles"

    class ProjectSettings(GeneralSettings, StaticSettings):
        pass

    to_django(ProjectSettings())
    assert locals()["DEBUG"] is False
    assert locals()["INSTALLED_APPS"] == ["django.contrib.admin", "django.contrib.auth"]
    assert locals()["LANGUAGE_CODE"] == "en-us"
    assert locals()["USE_TZ"] is True
    assert locals()["STATIC_URL"] == "/static/"
    assert locals()["STATIC_ROOT"] == "staticfiles"
    assert locals()["DATABASES"] == {
        "default": {
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": False,
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "hostname",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 5432,
            "USER": "user",
        }
    }


def test_to_django_recursive():
    class CSettings(BaseSettings):
        SETTING_C: str = "C"

    class BSettings(BaseSettings):
        SETTING_B: CSettings = CSettings()

    class NestedSettings(BaseSettings):
        SETTING_A: BSettings = BSettings()

    to_django(NestedSettings())

    diff = DeepDiff(locals()["SETTING_A"], {"SETTING_B": {"SETTING_C": "C"}})
    assert diff == {}


def test_to_django_with_secrets():
    class DBSettings(BaseSettings):
        PASSWORD: SecretStr

    class Settings(BaseSettings):
        DATABASE: DBSettings = DBSettings(PASSWORD="password")

    settings = Settings()
    to_django(settings)

    assert isinstance(settings.DATABASE.PASSWORD, SecretStr)
    assert "*" in str(settings.DATABASE.PASSWORD)
    assert locals()["DATABASE"]["PASSWORD"] == "password"


def test_to_django_with_secrets2():
    """
    Tests that a secret in the nested dict is unwrapped
    """

    class Settings(BaseSettings):
        USERNAME: str
        PASSWORD: SecretStr
        USERPASS: Dict = {}

        @field_validator("USERPASS")
        def populate_userpass(cls, value: Any, info: ValidationInfo):
            return {"USER": info.data.get("USERNAME"), "PASS": info.data.get("PASSWORD")}

    settings = Settings(USERNAME="user", PASSWORD="pass")
    to_django(settings)

    assert isinstance(settings.USERPASS["PASS"], SecretStr)
    assert "*" in str(settings.USERPASS["PASS"])
    assert locals()["USERPASS"]["PASS"] == "pass"


def test_to_django_nested_list():
    class ConnectionSettings(BaseSettings):
        HOST: str

    class Settings(BaseSettings):
        CONNECTIONS: List[ConnectionSettings] = [
            ConnectionSettings(HOST="google.com"),
            ConnectionSettings(HOST="github.com"),
            ConnectionSettings(HOST="stackoverflow.com"),
        ]

    settings = Settings()
    to_django(settings)

    diff = DeepDiff(
        locals()["CONNECTIONS"],
        [
            {"HOST": "google.com"},
            {"HOST": "github.com"},
            {"HOST": "stackoverflow.com"},
        ],
    )
    assert diff == {}
