"""Content-free observations of the context actually offered to a reply model."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING

from trubot.conversation import ConversationMessage, ReplyMode

if TYPE_CHECKING:
    from trubot.context_tools import ContextSkill

logger = logging.getLogger(__name__)
_ROUTES = {
    "get_up_conditions": "up_current",
    "get_up_last_night": "up_last_night",
    "clarify_up_night_location": "up_location",
}


def log_reply_context(
    messages: Sequence[ConversationMessage],
    selected: Sequence[ContextSkill],
    *,
    mode: ReplyMode,
    photo_available: bool,
    inspection_available: bool,
) -> None:
    """Emit fixed labels and counts only, never content, IDs or arbitrary tool names.

    This describes availability, not a tool execution, evidence quality, provider
    success or published Discord reply. It makes no change to the model request.
    """
    if not logger.isEnabledFor(logging.INFO):
        return
    routes = ",".join(sorted({_ROUTES.get(skill.name, "other") for skill in selected})) or "none"
    logger.info(
        "Reply context mode=%s routes=%s conversation=%d reference=%d focus=%d "
        "memory=%d images=%d photo=%s inspection=%s",
        mode.value,
        routes,
        sum(m.origin == "conversation" for m in messages),
        sum(m.origin == "reference" for m in messages),
        sum(m.origin == "focus" for m in messages),
        sum(m.origin == "memory" for m in messages),
        sum(len(m.images) for m in messages),
        photo_available,
        inspection_available,
    )
