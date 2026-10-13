"""Provider-neutral conversation types."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

MessageRole = Literal["user", "assistant"]
MessageOrigin = Literal["conversation", "memory", "reference", "focus"]


class MemoryAuthorScope(StrEnum):
    """Application-owned identity binding, never inferred from conversation text."""

    SOURCE_AUTHOR = "source_author"
    OTHER_AUTHOR = "other_author"
    UNKNOWN_AUTHOR = "unknown_author"


class ReplyMode(StrEnum):
    DIRECT = "direct"
    FOLLOW_UP = "follow_up"
    AMBIENT = "ambient"
    REACTION = "reaction"


@dataclass(frozen=True, slots=True)
class ConversationImage:
    data_url: str = field(repr=False)
    description: str


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    role: MessageRole
    content: str
    images: tuple[ConversationImage, ...] = field(default=(), repr=False)

    origin: MessageOrigin = "conversation"
    memory_author_scope: MemoryAuthorScope | None = None

    def as_input(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


def safety_identifier(guild_id: int | None, user_id: int) -> str:
    """Return a stable, privacy-preserving identifier for OpenAI safeguards."""

    scope = "dm" if guild_id is None else str(guild_id)
    value = f"discord:{scope}:{user_id}".encode()
    return hashlib.sha256(value).hexdigest()
