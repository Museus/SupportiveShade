from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class PersonalBestsSettings(BaseModel):
    enabled: bool
    channel_id: int
    emoji_id: int
    create_thread: bool


class VerifiedRunsSettings(BaseModel):
    class WatchedLeaderboard(BaseModel):
        channel_id: int
        game_name: str
        src_id: str

    enabled: bool
    poll_frequency: int
    leaderboards: dict[str, WatchedLeaderboard]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="/etc/supportive_shade/config.toml")

    personal_bests: list[PersonalBestsSettings]
    verified_runs: VerifiedRunsSettings

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