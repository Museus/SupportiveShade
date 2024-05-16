import datetime
import logging
from string import Template
from typing import Any, Iterator, Mapping

import requests

from . import schemas

logger = logging.getLogger("discord")


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
            raise

        user = schemas.User(**user_data)

        return user.names.international or "unknown"

    def get_leaderboard(
        self,
        game: str,
        category: str,
        subcategories: Mapping[str, str] = None,
        as_of: datetime.datetime = None,
    ):

        stringified_subcategories = (
            "&".join(
                [
                    f"var-{variable_id}={variable_value}"
                    for variable_id, variable_value in subcategories.items()
                ]
            )
            if subcategories
            else None
        )

        cache_key = (game, category, stringified_subcategories, as_of)

        if cached_board := self._cached_leaderboards.get(cache_key):
            return cached_board

        params = []
        if subcategories:
            params.append(stringified_subcategories)

        if as_of:
            params.append(f"date={as_of.isoformat()}")

        url = f"https://www.speedrun.com/api/v1/leaderboards/{game}/category/{category}{('?' + '&'.join(params)) if params else ''}"
        logger.info(url)
        response = requests.get(url).json()

        try:
            self._cached_leaderboards[cache_key] = response["data"]["runs"]
        except KeyError:
            logger.error("Failed to access leaderboard!")
            raise

        return self._cached_leaderboards[cache_key]

    def get_game_icon_url(self, game):
        url = f"https://www.speedrun.com/api/v1/games/{game}"
        response = requests.get(url).json()
        return response["data"]["assets"]["icon"]["uri"]

    def get_latest_run(self, game: str):
        url = f"https://www.speedrun.com/api/v1/runs?game={game}&status=verified&orderby=verify-date&direction=desc&max=1&embed=game,category.variables,players,level"
        response = requests.get(url).json()
        return schemas.Run(**response["data"][0])

    def get_verified_runs(
        self, game: str, since: datetime.datetime | None
    ) -> Iterator[schemas.Run]:
        # Any time we're fetching verified runs, we should clear the cached leaderboards
        self._cached_leaderboards = {}

        url = f"https://www.speedrun.com/api/v1/runs?game={game}&status=verified&orderby=verify-date&max=200&embed=game,category.variables,players,level"
        if since:
            url += "&direction=desc"
        else:
            url += "&direction=asc"

        verify_date_template = Template("${verify_date}+00:00")

        full_list = []
        should_break = False
        while True:

            response = requests.get(url).json()
            for run in response["data"]:
                if (not since) or (
                    datetime.datetime.fromisoformat(
                        # verify_date_template.substitute(
                        # verify_date=run["status"]["verify-date"]
                        run["status"]["verify-date"]
                        # )
                    ).replace(tzinfo=datetime.timezone.utc)
                    > since
                ):
                    full_list.append(schemas.Run(**run))
                else:
                    should_break = True
                    break

            if should_break:
                break

            for link in response["pagination"]["links"]:
                if link["rel"] == "next":
                    url = link["uri"]

        for run in reversed(full_list):
            yield run

    def get_game_variables(self, game: str) -> dict[str, Any]:
        url = f"https://www.speedrun.com/api/v1/games/{game}/variables"

        try:
            return requests.get(url).json()["data"]
        except Exception:
            return {}


src_api = SpeedrunApi()
