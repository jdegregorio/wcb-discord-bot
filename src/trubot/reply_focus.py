"""Bounded human context for an uninterrupted conversational follow-up."""

import re
from collections.abc import Sequence

from trubot.conversation import REFERENCE_PREFIX, ConversationMessage

MAX_FOCUS_CHARS = 600


def preceding_human_turn(messages: Sequence[ConversationMessage]) -> str:
    """Return a human setup, never memory, detached reference or a bot-created subject."""
    conversation = [message for message in messages if message.origin == "conversation"]
    if not conversation or conversation[-1].role != "assistant":
        return ""
    # An intervening human turn means the previous bot exchange is no longer immediate.
    # Its nearest preceding human supplies setup; the bot answer is not human evidence.
    for message in reversed(conversation[:-1]):
        if message.role == "user":
            return message.content[:MAX_FOCUS_CHARS]
    return ""


# Match complete topic-free follow-ups, not isolated pronouns inside a new subject.
_MEMORY_FOLLOWUP = re.compile(
    r"(?:(?:and|so|okay|ok|well) )*"
    r"(?:what (?:do|would) you (?:think|do|suggest|recommend)"
    r"(?: (?:about|of|with) (?:that|this|it|those|them))?"
    r"|how would you (?:handle|approach|respond to|deal with|think about) "
    r"(?:that|this|it|those|them)"
    r"|(?:which|what) (?:one|option)(?: would you (?:choose|pick|prefer))?"
    r"|tell me more(?: about (?:that|this|it))?"
    r"|why(?: (?:that|this|not))?"
    r"|what about (?:that|this|it|those|them))"
)


def memory_followup_query(request: str, messages: Sequence[ConversationMessage]) -> str:
    """Use a complete explicit or immediate human setup as a search key, never evidence.

    Original request remains the model focus. A freshly fetched explicit human
    reply reference wins over chronology. Bot/memory/visual text cannot establish
    a subject, and no setup is personal evidence. No multi-hop resolution.
    """
    normalized = " ".join(request.casefold().removeprefix("🤖").strip().split())
    normalized = normalized.removeprefix("@trubot ").rstrip("?!., ")
    if not _MEMORY_FOLLOWUP.fullmatch(normalized):
        return request
    references = [m for m in messages if m.origin == "reference"]
    if references:
        # The transport supplies at most one freshly fetched same-channel reference.
        # Invalid/unavailable/bot references block unrelated chronological fallback.
        if len(references) != 1:
            return request
        reference = references[0]
        if (
            reference.role != "user"
            or reference.author_user_id is None
            or reference.images
            or not reference.content.startswith(REFERENCE_PREFIX)
            or "[message with no text]" in reference.content
            or "[image attached]" in reference.content
            or "image pixels unavailable" in reference.content
        ):
            return request
        return _complete_setup(reference.content.removeprefix(REFERENCE_PREFIX), request)
    conversation = [m for m in messages[-8:] if m.origin == "conversation"]
    if (
        len(conversation) < 2
        or conversation[-1].role != "assistant"
        or conversation[-2].role != "user"
    ):
        return request
    return _complete_setup(conversation[-2].content, request)


def _complete_setup(content: str, request: str) -> str:
    setup = content.split(": ", 1)[-1].strip()
    # Truncation could drop a closing qualification or accidentally join phrases.
    if not setup or len(setup) > MAX_FOCUS_CHARS or setup.endswith("…"):
        return request
    return setup
