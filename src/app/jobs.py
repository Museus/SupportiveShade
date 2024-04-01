from abc import ABC, abstractmethod
from discord import Emoji, Message, TextChannel
import logging

from client import client
from settings import PersonalBestsSettings

logger = logging.getLogger("discord")


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
                thread_title = message.content[:50]
                if len(thread_title) < len(message.content):
                    thread_title += "..."
            else:
                thread_title = f"Discuss {message.author}'s PB here!"

            await message.create_thread(name=thread_title)