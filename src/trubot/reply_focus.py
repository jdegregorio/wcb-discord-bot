"""Bounded human context for an uninterrupted conversational follow-up."""

from collections.abc import Sequence

from trubot.conversation import ConversationMessage

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
