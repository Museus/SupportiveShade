import logging
import os

import discord

from jobs import Watcher, HandlePersonalBest


API_TOKEN = os.getenv("API_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
hooks: list[Watcher] = []

logger = logging.getLogger("discord")


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")

    # Register Personal Best Reactions
    logger.info("Initializing Personal Best Reactions...")
    pb_emoji = client.get_emoji(756150298803830897)
    pb_channel = client.get_channel(1221459166904979507)
    hooks.append(HandlePersonalBest(pb_emoji, pb_channel))
    logger.info(
        "Reacting to images and videos in %s with Emoji: %s and creating a thread", pb_channel, pb_emoji
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for hook in hooks:
        if hook.should_act(message):
            await hook.act(message)


client.run(API_TOKEN)
