import datetime
import logging
from string import Template
from typing import Mapping

import requests

from . import schemas

logger = logging.getLogger()


class SpeedrunApi:
    def __init__(self):
        self._cached_leaderboards = {}

    def get_user_name_from_id(self, user_id: str) -> str:
        try:
            user_data = requests.get(
                f"https://www.speedrun.com/api/v1/users/{user_id}"
            ).json()["data"]
        except Exception:
            logger.exception("Failed to get user!")

        user = schemas.User(**user_data)

        return user.names.international or "unknown"

    def get_leaderboard(
        self, game: str, category: str, subcategories: Mapping[str, str] = None
    ):
        stringified_subcategories = (
            "&".join(
                [
                    f"var-{variable[0]}={variable[1]}"
                    for variable in sorted(subcategories.items())
                ]
            )
            if subcategories
            else None
        )

        cache_key = (game, category, stringified_subcategories)

        if cached_board := self._cached_leaderboards.get(cache_key):
            return cached_board

        url = f"https://www.speedrun.com/api/v1/leaderboards/{game}/category/{category}{('?' + stringified_subcategories) if stringified_subcategories else ''}"
        response = requests.get(url).json()

        self._cached_leaderboards[cache_key] = response["data"]["runs"]

        return self._cached_leaderboards[cache_key]

    def get_game_icon_url(self, game):
        url = f"https://www.speedrun.com/api/v1/games/{game}"
        response = requests.get(url).json()
        return response["data"]["assets"]["icon"]["uri"]

    def get_latest_run(self, game: str):
        url = f"https://www.speedrun.com/api/v1/runs?game={game}&status=verified&orderby=verify-date&direction=desc&max=1&embed=game,category.variables,players,level"
        response = requests.get(url).json()
        return schemas.Run(**response["data"][0])

    def get_verified_runs(self, game: str, since: datetime.datetime | None):
        # Any time we're fetching verified runs, we should clear the cached leaderboards
        self._cached_leaderboards = {}

        url = f"https://www.speedrun.com/api/v1/runs?game={game}&status=verified&orderby=verify-date&max=200&embed=game,category.variables,players,level"
        if since:
            url += "&direction=desc"
        else:
            url += "&direction=asc"

        verify_date_template = Template("${verify_date}+00:00")

        while True:
            response = requests.get(url).json()
            for run in response["data"]:
                if (not since) or (
                    datetime.datetime.fromisoformat(
                        verify_date_template.substitute(
                            verify_date=run["status"]["verify-date"]
                        )
                    )
                    > since
                ):
                    yield schemas.Run(**run)
                else:
                    return

            for link in response["pagination"]["links"]:
                if link["rel"] == "next":
                    url = link["uri"]


src_api = SpeedrunApi()
