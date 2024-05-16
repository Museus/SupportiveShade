from verified_runs.api.api import src_api
from client import client
from verified_runs.runs import VerifiedHadesRun
from verified_runs.api.schemas import Run
import datetime
from typing import Any, Iterator
import logging
import json
import asyncio

logger = logging.getLogger("discord")


class CachedLeaderboardData:
    verifiers: dict[str, dict]


class WatchedLeaderboard:
    game_name: str
    get_since: datetime
    channel_id: str
    poll_frequency: int
    game_variables: dict[str, Any]

    def __init__(
        self,
        game_name: str,
        src_id: str,
        channel_id: str,
        poll_frequency: int,
        start_timestamp: datetime.datetime = None,
    ):
        self.game_name = game_name
        self.game_id = src_id
        self.channel = client.get_channel(channel_id)
        self.poll_frequency = poll_frequency

        self.get_since = (start_timestamp or datetime.datetime.now()).replace(
            tzinfo=datetime.timezone.utc
        )

        self.game_variables = src_api.get_game_variables(src_id)

    @property
    def verified_runs(self) -> Iterator[Run]:
        for run in src_api.get_verified_runs(self.game_id, since=self.get_since):
            yield run

    async def handle_new_runs(self):
        try:
            with open(
                "/var/lib/supportive_shade/posted_runs.json", "r"
            ) as posted_runs_file:
                already_posted_runs: list[str] = json.load(posted_runs_file)
        except Exception:
            logger.warning(
                "Failed to load already posted runs, defaulting to empty list"
            )
            already_posted_runs = []

        logger.info("Polling %s for runs since %s", self.game_name, self.get_since)
        for run in self.verified_runs:
            if run.id in already_posted_runs:
                logger.info("Skipping already posted run %s", run.id)
                continue

            parsed_run = VerifiedHadesRun(run, game_variables=self.game_variables)

            logger.info("Posting run %s", parsed_run.run_from_api.id)

            await self.channel.send(embed=parsed_run.to_embed())
            already_posted_runs.append(parsed_run.run_from_api.id)
            self.get_since = parsed_run.date_verified

            try:
                with open(
                    "/var/lib/supportive_shade/posted_runs.json", "w+"
                ) as posted_runs_file:
                    json.dump(already_posted_runs, posted_runs_file)
            except Exception:
                print("Failed to save already posted runs!")


    async def start_watching(self):
        while True:
            await self.handle_new_runs()
            logger.info("Handled new %s runs", self.game_name)
            await asyncio.sleep(self.poll_frequency)


class LeaderboardWatcher:
    watched_leaderboards: dict[str, WatchedLeaderboard]

    def __init__(self):
        self.watched_leaderboards = {}

    async def add_game(
        self,
        game_name: str,
        src_id: str,
        channel_id: str,
        poll_frequency: int,
        start_timestamp: datetime.datetime,
        include_history: bool = False,
    ) -> WatchedLeaderboard:
        """Create SpeedrunWatcher for the specified game and add it to
        `watched_leaderboards`

        Parameters
        ----------
        game_name : str
            name of game to watch, as defined by the speedrun.com URL
        follow_channel_id : str
            id of channel for messages to be posted in
        """

        new_board = WatchedLeaderboard(
            game_name, src_id, channel_id, poll_frequency, start_timestamp
        )
        self.watched_leaderboards[game_name] = new_board
        await new_board.channel.send(
            f"Back online! Now watching for new {game_name} runs!"
        )
        if include_history:
            await new_board.channel.send(
                f"This channel will also contain all previous {game_name} runs!"
            )

        return new_board

    async def start_all_watched_leaderboards(self):
        """Handle new runs for currently watched leaderboards"""
        for watcher in self.watched_leaderboards.values():
            asyncio.create_task(watcher.start_watching())
