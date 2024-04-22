from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Names(BaseModel):
    international: str
    japanese: Optional[str] = None


class Color(BaseModel):
    light: str
    dark: str


class GradientNameStyle(BaseModel):
    style: str  # This appears to always be a gradient
    color_from: Color = Field(..., alias="color-from")
    color_to: Color = Field(..., alias="color-to")


class SolidNameStyle(BaseModel):
    style: str
    color: Color


class Country(BaseModel):
    code: str
    names: Names


class Region(BaseModel):
    code: str
    names: Names


class Location(BaseModel):
    country: Optional[Country] = None
    region: Optional[Region] = None


class Social(BaseModel):
    uri: str


class Asset(BaseModel):
    uri: Optional[str] = None


class Assets(BaseModel):
    icon: Asset
    supporterIcon: Optional[Asset] = None
    image: Asset


class Link(BaseModel):
    rel: str
    uri: str


class User(BaseModel):
    id: str
    names: Names
    supporterAnimation: bool
    pronouns: Optional[str] = None
    weblink: str
    name_style: GradientNameStyle | SolidNameStyle = Field(..., alias="name-style")
    role: str
    signup: str
    location: Location
    twitch: Optional[Social] = None
    hitbox: Optional[Social] = None
    youtube: Optional[Social] = None
    twitter: Optional[Social] = None
    speedrunslive: Optional[Social] = None
    assets: Assets
    links: list[Link]
