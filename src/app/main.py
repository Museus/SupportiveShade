import logging
import os

from discord import Message

from client import client
from jobs import Watcher, HandlePersonalBest
from settings import settings


logger = logging.getLogger("discord")
hooks: list[Watcher] = []


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")

    # Register Personal Best Reactions
    if settings.personal_bests.enabled:
        logger.info("Initializing Personal Best Reactions...")

        try:
            pb_handler = HandlePersonalBest(settings.personal_bests)
        except Exception:
            logger.exception("Failed to initialize Personal Bests handler!")
        else:
            hooks.append(pb_handler)
            logger.info(
                "[HandlePersonalBest] Handling personal bests in #%s with Emoji: %s",
                pb_handler.channel,
                pb_handler.emoji,
            )


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    for hook in hooks:
        if hook.should_act(message):
            await hook.act(message)

client.run(token=os.getenv("API_TOKEN"))
