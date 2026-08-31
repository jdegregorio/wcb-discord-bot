"""Provider-neutral conversation types."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

MessageRole = Literal["user", "assistant"]


class ReplyMode(StrEnum):
    DIRECT = "direct"
    AMBIENT = "ambient"
    REACTION = "reaction"


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    role: MessageRole
    content: str

    def as_input(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


def safety_identifier(guild_id: int | None, user_id: int) -> str:
    """Return a stable, privacy-preserving identifier for OpenAI safeguards."""

    scope = "dm" if guild_id is None else str(guild_id)
    value = f"discord:{scope}:{user_id}".encode()
    return hashlib.sha256(value).hexdigest()
