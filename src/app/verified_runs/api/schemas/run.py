from typing import Optional

from pydantic import BaseModel, Field

from .user import User


class GameNames(BaseModel):
    international: str
    japanese: Optional[str]
    twitch: Optional[str]


class Ruleset(BaseModel):
    show_milliseconds: bool = Field(..., alias="show-milliseconds")
    require_verification: bool = Field(..., alias="require-verification")
    require_video: bool = Field(..., alias="require-video")
    run_times: list[str] = Field(..., alias="run-times")
    default_time: str = Field(..., alias="default-time")
    emulators_allowed: bool = Field(..., alias="emulators-allowed")


class Asset(BaseModel):
    uri: Optional[str] = None


class GameAssets(BaseModel):
    logo: Optional[Asset] = None
    cover_tiny: Optional[Asset] = Field(None, alias="cover-tiny")
    cover_small: Optional[Asset] = Field(None, alias="cover-small")
    cover_medium: Optional[Asset] = Field(None, alias="cover-medium")
    cover_large: Optional[Asset] = Field(None, alias="cover-large")
    icon: Optional[Asset] = None
    trophy_1st: Optional[Asset] = Field(None, alias="trophy-1st")
    trophy_2nd: Optional[Asset] = Field(None, alias="trophy-2nd")
    trophy_3rd: Optional[Asset] = Field(None, alias="trophy-3rd")
    trophy_4th: Optional[Asset] = Field(None, alias="trophy-4th")
    background: Optional[Asset] = None
    foreground: Optional[Asset] = None


class Link(BaseModel):
    rel: str
    uri: str


class GameData(BaseModel):
    id: str
    names: GameNames
    boostReceived: int
    boostDistinctDonors: int
    abbreviation: str
    weblink: str
    discord: str
    released: int
    release_date: str = Field(..., alias="release-date")
    ruleset: Ruleset
    romhack: bool
    gametypes: list
    platforms: list[str]
    regions: list
    genres: list[str]
    engines: list
    developers: list[str]
    publishers: list[str]
    moderators: dict[str, str]
    created: str
    assets: GameAssets
    links: list[Link]


class Game(BaseModel):
    data: GameData


class Level(BaseModel):
    data: list


class Players(BaseModel):
    type: str
    value: int


class Scope(BaseModel):
    type: str


class VariableName(BaseModel):
    label: str


class Flags(BaseModel):
    miscellaneous: str


class Flags6(BaseModel):
    miscellaneous: bool


class VariableValueValues(BaseModel):
    label: str
    rules: Optional[str] = None


class VariableValues(BaseModel):
    field_note: str = Field(..., alias="_note")
    choices: Optional[dict[str, str]] = None
    values: dict[str, VariableValueValues]
    default: Optional[str] = None


class Variable(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    scope: Scope
    mandatory: bool
    user_defined: bool = Field(..., alias="user-defined")
    obsoletes: bool
    values: VariableValues
    is_subcategory: bool = Field(..., alias="is-subcategory")
    links: list[Link]


class Variables(BaseModel):
    data: list[Variable]


class CategoryData(BaseModel):
    id: str
    name: str
    weblink: str
    type: str
    rules: str
    players: Players
    miscellaneous: bool
    links: list[Link]
    variables: Variables


class Category(BaseModel):
    data: CategoryData


class Videos(BaseModel):
    links: list[Asset]


class Status(BaseModel):
    status: str
    examiner: str
    verify_date: str = Field(..., alias="verify-date")


class Times(BaseModel):
    primary: str
    primary_t: int
    realtime: Optional[str] = None
    realtime_t: Optional[int] = None
    realtime_noloads: Optional[str] = None
    realtime_noloads_t: Optional[int] = None
    ingame: Optional[str] = None
    ingame_t: Optional[int] = None


class System(BaseModel):
    platform: str
    emulated: bool
    region: Optional[str] = None


class Players(BaseModel):
    data: list[User]


class Reference(BaseModel):
    uri: str
    rel: str


class Run(BaseModel):
    id: str
    weblink: str
    game: Game
    level: Level
    category: Category
    videos: Videos
    comment: Optional[str] = None
    status: Status
    players: Players
    date: str
    submitted: str
    times: Times
    system: System
    splits: Optional[Reference] = None
    values: Optional[dict[str, str]] = None
    links: list[Reference]
