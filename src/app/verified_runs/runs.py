from datetime import datetime
import json
from typing import Any, Mapping

import discord

from .api.api import src_api
from .util import seconds_to_readable


class VerifiedRun:
    run_from_api: Mapping[str, Any]

    _runner_id: str
    runner: str

    _duration: float | None
    duration: str | None

    leaderboard_rank: int | None
    _date_played: datetime | None
    _verified_by: str | None
    _date_verified: datetime | None
    _url: str | None
    category: str | None
    category_id: str | None

    def __init__(self, run_from_api: Mapping[str, Any]):
        self.run_from_api = run_from_api
        if not self.run_from_api["status"]["status"] == "verified":
            raise Exception("Tried to parse an unverified run!")

        self.game = self.run_from_api["game"]["data"]["id"]
        self.category_id = self.run_from_api["category"]["data"]["id"]
        self.category = self.run_from_api["category"]["data"]["name"]

        # Get runner info
        self._runner_id = self.run_from_api["players"]["data"][0]["id"]
        self.runner = src_api.get_user_name_from_id(self._runner_id)

        self._duration_in_seconds = self.run_from_api["times"]["primary_t"]
        self.duration = seconds_to_readable(self._duration_in_seconds)

        run_variables = self.run_from_api["values"]
        leaderboard_subcategories = {
            variable["id"]: variable
            for variable in self.run_from_api["category"]["data"]["variables"]["data"]
            if variable["is-subcategory"]
        }

        self._subcategories = {
            variable_id: variable_value
            for variable_id, variable_value in run_variables.items()
            if variable_id in leaderboard_subcategories.keys()
        }

        self.subcategories = [
            leaderboard_subcategories[variable_id]["values"]["values"][variable_value][
                "label"
            ]
            for variable_id, variable_value in run_variables.items()
            if variable_id in leaderboard_subcategories.keys()
        ]

        leaderboard = src_api.get_leaderboard(
            game=self.game,
            category=self.category_id,
            subcategories=self._subcategories,
        )

        for idx, run in enumerate(leaderboard):
            if run["run"]["id"] == self.run_from_api["id"]:
                self.leaderboard_rank = idx
                break

        self._date_played = None
        self._verified_by = None

    @property
    def date_played(self):
        if not hasattr(self, "_date_played"):
            self._date_played = self.run_from_api["date"]

        return self._date_played

    @property
    def verified_by(self):
        if not hasattr(self, "_verified_by"):
            verifier_id = self.run_from_api["status"]["examiner"]
            self._verified_by = src_api.get_user_name_from_id(verifier_id)

        return self._verified_by

    @property
    def date_verified(self):
        if not hasattr(self, "_date_verified"):
            self._date_verified = datetime.strptime(
                self.run_from_api["status"]["verify-date"], "%Y-%m-%dT%H:%M:%SZ"
            )

        return self._date_verified

    @property
    def run_title(self):
        return "%s - %s - %s" % (
            self.run_from_api["game"]["data"]["names"]["international"],
            self.run_from_api["category"]["data"]["name"],
            ", ".join(self.subcategories),
        )

    def to_embed(self) -> discord.Embed:
        message_embed = discord.Embed(timestamp=self.date_verified)

        message_embed.set_author(name=self.run_title, icon_url="")

        message_embed.add_field(name="Runner", value=self.runner, inline=True)

        message_embed.add_field(name="Time", value=self.duration)
        message_embed.add_field(
            name="Leaderboard Rank", value=self.leaderboard_rank, inline=True
        )

        message_embed.add_field(name="Date Played", value=self.duration)

        message_embed.set_footer(
            text=f"Verified by {self.verified_by}",
            icon_url="https://www.speedrun.com/images/favicon.png",
        )

        return message_embed


class VerifiedHadesRun(VerifiedRun):
    _aspect: str | None
    _aspect_name: str | None
    _aspect_rank: int | None
    _date_played: str | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("hades_variables.json") as variables_file:
            self.game_variables = json.load(variables_file)

    @property
    def aspect(self):
        if not hasattr(self, "_aspect"):
            aspect_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] != "Aspect"
            }

            for variable_id, variable_value in self.run_from_api["values"].items():
                if variable_id in aspect_variables:
                    self._aspect_key = variable_id
                    self._aspect = variable_value
                    break

        return (self._aspect_key, self._aspect)

    @property
    def weapon(self):
        if not hasattr(self, "_weapon"):
            weapon_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] not in ["Weapon", "Weapon (OwO)"]
            }

            for variable_id, variable_value in self.run_from_api["values"].items():
                if variable_id in weapon_variables:
                    self._weapon_key = variable_id
                    self._weapon = variable_value
                    break

        return (self._weapon_key, self._weapon)

    @property
    def aspect_name(self):
        if not hasattr(self, "_aspect_name"):
            aspect_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] == "Aspect"
            }

            for variable_id, variable_value in self.run_from_api["values"].items():
                if variable_id in aspect_variables:
                    self._aspect_name = self.game_variables[variable_id]["values"][
                        variable_value
                    ]["label"]

        return self._aspect_name

    @property
    def weapon_name(self):
        if not hasattr(self, "_weapon_name"):
            weapon_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] == "Weapon"
            }

            for variable_id, variable_value in self.run_from_api["values"].items():
                if variable_id in weapon_variables:
                    self._weapon_name = self.game_variables[variable_id]["values"][
                        variable_value
                    ]["label"]

        return self._weapon_name

    @property
    def aspect_rank(self):
        if not hasattr(self, "_aspect_rank"):
            if not self.aspect:
                self._aspect_rank = "-1"

            subcategories = self._subcategories
            aspect_key, aspect_value = self.aspect
            subcategories[aspect_key] = aspect_value

            if not getattr(self, "_aspect_rank", None):
                leaderboard = src_api.get_leaderboard(
                    game=self.game,
                    category=self.category_id,
                    subcategories=self._subcategories,
                )

                for idx, run in enumerate(leaderboard):
                    if run["run"]["id"] == self.run_from_api["id"]:
                        self._aspect_rank = idx
                        break

        return self._aspect_rank

    @property
    def weapon_rank(self):
        if not hasattr(self, "_weapon_rank"):
            if not self.weapon:
                self._weapon_rank = "-1"

            subcategories = self._subcategories
            weapon_key, weapon_value = self.weapon
            subcategories[weapon_key] = weapon_value

            if not getattr(self, "_weapon_rank", None):
                leaderboard = src_api.get_leaderboard(
                    game=self.game,
                    category=self.category_id,
                    subcategories=self._subcategories,
                )

                for idx, run in enumerate(leaderboard):
                    if run["run"]["id"] == self.run_from_api["id"]:
                        self._weapon_rank = idx
                        break

        return self._weapon_rank

    def to_embed(self) -> discord.Embed:
        message_embed = discord.Embed(timestamp=self.date_verified)

        message_embed.set_author(
            name=self.run_title,
            icon_url="https://www.speedrun.com/static/theme/zr0g008m/favicon.png?v=7f661bb",
        )

        message_embed.add_field(name="Runner", value=self.runner, inline=True)
        if self.aspect_name:
            message_embed.add_field(name="Aspect", value=self.aspect_name, inline=True)
        elif self.weapon_name:
            message_embed.add_field(name="Weapon", value=self.aspect_name, inline=True)

        message_embed.add_field(name="Time", value=self.duration)
        message_embed.add_field(
            name="Leaderboard Rank", value=self.leaderboard_rank, inline=True
        )
        message_embed.add_field(
            name="Aspect Rank", value=self.aspect_rank or "Unknown", inline=True
        )

        message_embed.add_field(name="Date Played", value=self.duration)

        message_embed.set_footer(text=f"Verified by {self.verified_by}", icon_url="")

        return message_embed
