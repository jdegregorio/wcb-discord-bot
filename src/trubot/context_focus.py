"""Resolve one complete location answer against the same human's immediate question."""

from __future__ import annotations

import re
from collections.abc import Sequence

from trubot.conversation import ConversationMessage, ReplyMode

_LOCATION = re.compile(
    r"(?:and )?(?:(?:what|how) about )?(?:the )?(marquette|munising|keweenaw)[?!. ]*",
    re.IGNORECASE,
)


def location_question(
    target: str | None,
    messages: Sequence[ConversationMessage],
    *,
    mode: ReplyMode,
    requester_user_id: int | None,
) -> str | None:
    """Supply a search subject only. Bot wording and peer labels never supply evidence.

    A reference/focus or intervening human breaks adjacency. Full questions are
    selected separately by the existing skill contracts; never reconstruct clipped
    text or inherit a date from the bot's answer.
    """
    if not target or mode not in {ReplyMode.DIRECT, ReplyMode.FOLLOW_UP}:
        return None
    text = target.split(": ", 1)[-1].strip().removeprefix("🤖").strip()
    match = _LOCATION.fullmatch(text)
    if match is None or requester_user_id is None:
        return None
    # Memory packets are application-owned additions, not conversation turns.
    turns = [m for m in messages if m.origin != "memory"]
    if len(turns) < 2:
        return None
    human, bot = turns[-2:]
    if (
        human.origin != "conversation"
        or bot.origin != "conversation"
        or human.role != "user"
        or bot.role != "assistant"
        or human.author_user_id != requester_user_id
        or human.images
        or bot.images
    ):
        return None
    question = human.content.split(": ", 1)[-1].strip().removeprefix("🤖").strip()
    if not question or len(question.encode()) > 600 or question.endswith("…"):
        return None
    if re.search(r"\b(?:now|current(?:ly)?|tonight|today|latest)\b", question, re.I) and re.search(
        r"\b(?:last night|yesterday (?:night|evening)|previous night)\b", question, re.I
    ):
        return None
    return question + " Location: " + match.group(1).capitalize() + "."
