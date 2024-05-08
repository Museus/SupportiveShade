from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VerifiedRunsSettings(BaseModel):
    class WatchedLeaderboard(BaseModel):
        channel_id: int
        game_name: str
        src_id: str
        start_timestamp: Optional[datetime] = None

    enabled: bool
    poll_frequency: int
    leaderboards: list[WatchedLeaderboard]
