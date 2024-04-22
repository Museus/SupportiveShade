import pathlib
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class SpeedrunApiTestUserSettings(BaseModel):
    id: str
    name: str


class SpeedrunApiTestGameSettings(BaseModel):
    id: str
    name: str


class SpeedrunApiValidationUserSettings(BaseModel):
    valid_users: pathlib.Path
    invalid_users: pathlib.Path


class SpeedrunApiValidationSettings(BaseModel):
    user: SpeedrunApiValidationUserSettings


class SpeedrunApiSettings(BaseModel):
    test_user: SpeedrunApiTestUserSettings
    test_game: SpeedrunApiTestGameSettings
    validation: SpeedrunApiValidationSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="./tests/config.toml")

    speedrun_api: SpeedrunApiSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = Settings()