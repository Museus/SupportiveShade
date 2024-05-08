from datetime import datetime, timezone
import logging
import os

from discord import Message

from client import client
from jobs import Watcher, HandlePersonalBest
from verified_runs.main import LeaderboardWatcher
from settings import settings


logger = logging.getLogger("discord")
hooks: list[Watcher] = []


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")

    # Register Personal Best Reactions
    for pb_settings in settings.personal_bests:
        if not pb_settings.enabled:
            continue

        logger.info(
            "Initializing Personal Best Reactions for channel %s...",
            pb_settings.channel_id,
        )

        try:
            pb_handler = HandlePersonalBest(pb_settings)
        except Exception:
            logger.exception("Failed to initialize Personal Bests handler!")
        else:
            hooks.append(pb_handler)
            logger.info(
                "[HandlePersonalBest] Handling personal bests in #%s with Emoji: %s",
                pb_handler.channel,
                pb_handler.emoji,
            )

    # Watch leaderboards for new runs
    if settings.verified_runs.enabled:
        leaderboard_watcher = LeaderboardWatcher()
        for leaderboard_to_watch in settings.verified_runs.leaderboards:
            leaderboard_handler = await leaderboard_watcher.add_game(
                leaderboard_to_watch.game_name,
                leaderboard_to_watch.src_id,
                leaderboard_to_watch.channel_id,
                settings.verified_runs.poll_frequency,
                leaderboard_to_watch.start_timestamp,
            )

            logger.info(
                "[VerifiedRuns] Watching %s verified runs in #%s",
                leaderboard_to_watch.game_name,
                leaderboard_handler.channel,
            )

        await leaderboard_watcher.start_all_watched_leaderboards()


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    for hook in hooks:
        if hook.should_act(message):
            await hook.act(message)


client.run(token=os.getenv("API_TOKEN"))
