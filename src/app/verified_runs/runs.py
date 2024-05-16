from datetime import datetime
import json
from typing import Any, Mapping
import logging

import discord

from .api.api import src_api
from .util import seconds_to_readable
from .api.schemas import Run

logger = logging.getLogger("discord")


class VerifiedRun:
    run_from_api: Run

    _runner_id: str
    runner: str

    _duration: float | None
    duration: str | None

    leaderboard_rank: int | None
    _date_played: datetime | None
    _verified_by: str | None
    _date_verified: datetime | None
    category: str | None
    category_id: str | None

    game_variables: dict[str, Any]

    url: str

    def __init__(self, run_from_api: Run, game_variables: dict[str, Any] = None):
        self.run_from_api = run_from_api
        if not self.run_from_api.status.status == "verified":
            raise Exception("Tried to parse an unverified run!")

        self.game = self.run_from_api.game.data.id
        self.category_id = self.run_from_api.category.data.id
        self.category = self.run_from_api.category.data.name

        # Get runner info
        self._runner_id = self.run_from_api.players.data[0].id
        self.runner = src_api.get_user_name_from_id(self._runner_id)
        self.runner_url = self.run_from_api.players.data[0].weblink

        self._duration_in_seconds = self.run_from_api.times.primary_t
        self.duration = seconds_to_readable(self._duration_in_seconds)

        run_variables = self.run_from_api.values
        leaderboard_subcategories = {
            variable.id: variable
            for variable in self.run_from_api.category.data.variables.data
            if variable.is_subcategory
        }

        self._subcategories = {
            variable_id: variable_value
            for variable_id, variable_value in run_variables.items()
            if variable_id in leaderboard_subcategories.keys()
        }

        self.subcategories = [
            leaderboard_subcategories[variable_id]
            .values.values.get(variable_value)
            .label
            for variable_id, variable_value in run_variables.items()
            if variable_id in leaderboard_subcategories.keys()
        ]

        attempts = 0
        while attempts < 5:
            try:
                leaderboard = src_api.get_leaderboard(
                    game=self.game,
                    category=self.category_id,
                    subcategories=self._subcategories,
                    as_of=self.date_verified,
                )
            except Exception:
                attempts += 1
            else:
                break

        for idx, run in enumerate(leaderboard):
            if run["run"]["id"] == self.run_from_api.id:
                self.leaderboard_rank = run["place"]
                break

        if not hasattr(self, "leaderboard_rank"):
            self.leaderboard_rank = -1

        self._date_played = None
        self._verified_by = None

        self.game_variables = game_variables or {}
        self.url = run_from_api.weblink

    @property
    def date_played(self):
        if not self._date_played:
            self._date_played = self.run_from_api.date

        return self._date_played

    @property
    def verified_by(self):
        if not self._verified_by:
            attempts = 0
            verifier_id = self.run_from_api.status.examiner
            while not self._verified_by and attempts < 5:
                attempts += 1
                try:
                    self._verified_by = src_api.get_user_name_from_id(verifier_id)
                    logger.info("Got verifier %s", self._verified_by)
                except Exception:
                    self._verified_by = None

            if not self._verified_by:
                self._verified_by = verifier_id
                logger.info("Falling back to verifier ID: %s", verifier_id)


        return self._verified_by

    @property
    def date_verified(self):
        if not hasattr(self, "_date_verified"):
            self._date_verified = datetime.strptime(
                self.run_from_api.status.verify_date, "%Y-%m-%dT%H:%M:%SZ"
            )

        return self._date_verified

    @property
    def run_title(self):
        return "%s - %s - %s" % (
            self.run_from_api.game.data.names.international,
            self.run_from_api.category.data.name,
            ", ".join(self.subcategories),
        )

    def to_embed(self) -> discord.Embed:
        message_embed = discord.Embed(timestamp=self.date_verified)

        message_embed.set_author(name=self.run_title, icon_url="")

        message_embed.add_field(
            name="Runner", value=f"[{self.runner}]({self.runner_url})", inline=True
        )

        message_embed.add_field(name="Time", value=self.duration)
        message_embed.add_field(
            name="Leaderboard Rank", value=self.leaderboard_rank, inline=True
        )

        message_embed.add_field(name="Date Played", value=self.date_played)

        message_embed.add_field(
            name="", value=f"[Click here to see the run!]({self.url})"
        )
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

    @property
    def aspect(self):
        if not hasattr(self, "_aspect"):
            aspect_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] == "Aspect"
            }

            for variable_id, variable_value in self.run_from_api.values.items():
                if variable_id in aspect_variables:
                    self._aspect_key = variable_id
                    self._aspect = variable_value
                    break

        if not hasattr(self, "_aspect"):
            return None

        return (self._aspect_key, self._aspect)

    @property
    def weapon(self):
        if not hasattr(self, "_weapon"):
            weapon_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] not in ["Weapon", "Weapon (OwO)"]
            }

            for variable_id, variable_value in self.run_from_api.values.items():
                if variable_id in weapon_variables:
                    self._weapon_key = variable_id
                    self._weapon = variable_value
                    break

        if not hasattr(self, "_weapon"):
            return None

        return (self._weapon_key, self._weapon)

    @property
    def aspect_name(self):
        if not hasattr(self, "_aspect_name"):
            aspect_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] == "Aspect"
            }

            for variable_id, variable_value in self.run_from_api.values.items():
                if variable_id in aspect_variables:
                    self._aspect_name = aspect_variables[variable_id]["values"][
                        "values"
                    ][variable_value]["label"]

        if not hasattr(self, "_aspect_name"):
            return "Unknown"

        return self._aspect_name

    @property
    def weapon_name(self):
        if not hasattr(self, "_weapon_name"):
            weapon_variables = {
                variable["id"]: variable
                for variable in self.game_variables
                if variable["name"] == "Weapon"
            }

            for variable_id, variable_value in self.run_from_api.values.items():
                if variable_id in weapon_variables:
                    self._weapon_name = weapon_variables[variable_id]["values"][
                        "values"
                    ][variable_value]["label"]

        if not hasattr(self, "_weapon_name"):
            return "Unknown"

        return self._weapon_name

    @property
    def aspect_rank(self):
        if not hasattr(self, "_aspect_rank"):
            if not self.aspect:
                self._aspect_rank = "-1"
            else:
                subcategories_and_aspect = self._subcategories
                aspect_key, aspect_value = self.aspect
                logger.info("Filtering aspect %s: %s", aspect_key, aspect_value)
                subcategories_and_aspect[aspect_key] = aspect_value

                leaderboard = src_api.get_leaderboard(
                    game=self.game,
                    category=self.category_id,
                    subcategories=subcategories_and_aspect,
                    as_of=self.date_verified,
                )

                for idx, run in enumerate(leaderboard):
                    if run["run"]["id"] == self.run_from_api.id:
                        self._aspect_rank = run["place"]
                        break

        return getattr(self, "_aspect_rank", None)

    @property
    def weapon_rank(self):
        if not hasattr(self, "_weapon_rank"):
            if not self.weapon:
                self._weapon_rank = "-1"
            else:
                subcategories = self._subcategories
                weapon_key, weapon_value = self.weapon
                subcategories[weapon_key] = weapon_value

                if not getattr(self, "_weapon_rank", None):
                    leaderboard = src_api.get_leaderboard(
                        game=self.game,
                        category=self.category_id,
                        subcategories=self._subcategories,
                        as_of=self.date_verified,
                    )

                    for idx, run in enumerate(leaderboard):
                        if run["run"]["id"] == self.run_from_api.id:
                            self._weapon_rank = run["place"]
                            break

        return self._weapon_rank

    def to_embed(self) -> discord.Embed:
        message_embed = discord.Embed(
            description=f"[Click here to see the run!]({self.url})",
            timestamp=self.date_verified,
        )

        message_embed.set_author(
            name=self.run_title,
            icon_url="https://www.speedrun.com/static/theme/zr0g008m/favicon.png?v=7f661bb",
        )

        message_embed.add_field(
            name="Runner", value=f"[{self.runner}]({self.runner_url})", inline=True
        )
        if self.aspect_name != "Unknown":
            message_embed.add_field(name="Aspect", value=self.aspect_name, inline=True)
        elif self.weapon_name != "Unknown":
            message_embed.add_field(name="Weapon", value=self.weapon_name, inline=True)

        message_embed.add_field(name="Time", value=self.duration)
        message_embed.add_field(
            name="Leaderboard Rank", value=self.leaderboard_rank if self.leaderboard_rank != -1 else "Obsolete", inline=True
        )

        if self.aspect_name != "Unknown":
            message_embed.add_field(
                name="Aspect Rank", value=self.aspect_rank or "Obsolete", inline=True
            )

        message_embed.add_field(name="Date Played", value=self.date_played)

        message_embed.set_footer(text=f"Verified by {self.verified_by}", icon_url="")

        return message_embed
