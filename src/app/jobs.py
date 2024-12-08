from abc import ABC, abstractmethod
from discord import Emoji, Message, TextChannel
from log_util import logger
import re

from client import client
from settings import PersonalBestsSettings


class Watcher(ABC):
    @abstractmethod
    def should_act(self, message: Message) -> bool:
        pass

    @abstractmethod
    def act(self, message: Message):
        if not self.should_act(message):
            return

        pass


class HandlePersonalBest(Watcher):
    enabled: bool
    emoji: Emoji
    channel: TextChannel
    create_thread: bool

    EMOTE_PATTERN = re.compile(r"<:(\S+):\d+>")

    def __init__(self, settings: PersonalBestsSettings):
        self.enabled = settings.enabled
        self.emoji = client.get_emoji(settings.emoji_id)
        self.channel = client.get_channel(settings.channel_id)
        self.create_thread = settings.create_thread

    def should_act(self, message: Message) -> bool:
        if not self.enabled:
            return False

        if message.channel is not self.channel:
            return False

        if not message.attachments:
            return False

        return any(
            "image" in attachment.content_type or "video" in attachment.content_type
            for attachment in message.attachments
        )

    async def act(self, message: Message):
        logger.debug("[HandlePersonalBest] Reacting to %s", message.id)
        await message.add_reaction(self.emoji)

        if self.create_thread:
            logger.debug("[HandlePersonalBest] Creating a thread!")
            if message.content:
                thread_title = message.content

                # Replace emote strings with names
                thread_title = re.sub(
                    self.EMOTE_PATTERN, lambda e: ":" + e.group(1) + ":", thread_title
                )

                # Trim down to 50 characters
                original_length = len(thread_title)
                thread_title = thread_title[:50]
                if len(thread_title) < original_length:
                    thread_title += "..."

            else:
                thread_title = f"Discuss {message.author}'s PB here!"

            await message.create_thread(name=thread_title)
