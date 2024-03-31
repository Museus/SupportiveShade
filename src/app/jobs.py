from abc import ABC, abstractmethod
from discord import TextChannel, Emoji, Message
import logging

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

    emoji: Emoji

    def __init__(self, emoji: Emoji, channel: TextChannel):
        self.emoji = emoji
        self.channel = channel

    def should_act(self, message: Message) -> bool:
        if message.channel is not self.channel:
            return False

        if not message.attachments:
            return False

        return any(
            "image" in attachment.content_type or "video" in attachment.content_type
            for attachment in message.attachments
        )

    async def act(self, message: Message):
        if not self.should_act(message):
            return

        logger.debug("Reacting to %s!", message.id)
        await message.add_reaction(self.emoji)

        logger.debug("Creating a thread!")
        if message.content:
            thread_title = message.content[:50]
            if len(thread_title) < len(message.content):
                thread_title += "..."
        else:
            thread_title = f"Discuss {message.author}'s PB here!"

        await message.create_thread(name=thread_title)