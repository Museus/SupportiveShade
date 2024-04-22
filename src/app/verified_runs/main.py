from .api.api import src_api
from .runs import VerifiedHadesRun
from settings import VerifiedRunsSettings
import datetime
import discord
from typing import Generator
import logging
import json

logger = logging.getLogger("discord")


class WatchedLeaderboard:
    game_name: str
    last_polled: datetime
    follow_channel_id: str

    def __init__(self, leaderboard_settings: VerifiedRunsSettings.WatchedLeaderboard):
        self.game_name = leaderboard_settings.game_name
        self.game_id = leaderboard_settings.src_id
        self.follow_channel_id = leaderboard_settings.channel_id

        self.last_polled = None

    def verified_runs(self, since: datetime.datetime | None) -> Generator[dict]:
        for run in src_api.get_verified_runs(self.game_id, since=since):
            yield run

    async def handle_new_runs(self, client: discord.Client):
        try:
            with open("posted_runs.json", "r") as posted_runs_file:
                already_posted_runs: list[str] = json.load(posted_runs_file)
        except Exception:
            logger.warning(
                "Failed to load already posted runs, defaulting to empty list"
            )
            already_posted_runs = []

        for run in self.verified_runs(since=self.last_polled):
            parsed_run = VerifiedHadesRun(run)
            logger.debug("Posting run %s", parsed_run.url)

            await client.get_channel(self.follow_channel_id).send(
                embed=parsed_run.to_embed()
            )
            already_posted_runs.append(parsed_run.id)

        try:
            with open("posted_runs.json", "w") as posted_runs_file:
                json.dump(already_posted_runs, posted_runs_file)
        except Exception:
            print("Failed to save already posted runs!")


watched_leaderboards: dict[str, WatchedLeaderboard] = {}


async def add_game_to_watchlist(
    game_name: str, follow_channel_id: str, include_history: bool = False
) -> None:
    """Create SpeedrunWatcher for the specified game and add it to
    `watched_leaderboards`

    Parameters
    ----------
    game_name : str
        name of game to watch, as defined by the speedrun.com URL
    follow_channel_id : str
        id of channel for messages to be posted in
    """
    game_watcher = WatchedLeaderboard(game_name)
    watched_leaderboards[game_name] = WatchedLeaderboard(
        game_name=game_name,
        handler=game_watcher,
        last_polled=(
            None if not include_history else datetime.datetime.now(datetime.UTC)
        ),
        follow_channel_id=follow_channel_id,
    )

    try:
        with open("watched.json", "r") as watched_file:
            json.dump(watched_leaderboards, watched_file)
    except Exception:
        print("Failed to save watched leaderboards!")


async def poll_all_watched_leaderboards(client: discord.Client):
    """Handle new runs for currently watched leaderboards"""
    for game_name, watcher in watched_leaderboards.items():
        logger.debug("Polling %s...", game_name)
        new_poll_time = datetime.datetime.now(datetime.UTC)
        watcher.handle_new_runs(client=client)
        watcher.last_polled = new_poll_time
