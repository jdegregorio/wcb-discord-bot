"""Conservative ordinary-reply length checks, never a semantic quality judge."""

from __future__ import annotations

import re
from collections.abc import Sequence

from trubot.conversation import ConversationMessage
from trubot.reply_presentation import dialogue_content, requested_quotation

_WORD = re.compile(r"\w+(?:['\u2019]\w+)*")
_QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”')
_END = re.compile(r"[.!?]+(?=\s|$)")
_ABBREVIATION = re.compile(
    r"(?:\b(?:mr|mrs|ms|dr|prof|sr|jr|st)|\be\.g|\bi\.e|\b[ap]\.m|\bu\.s)\.$", re.IGNORECASE
)
_EXPANDED_REQUEST = re.compile(
    r"\b(?:quot(?:e|ing|ation)|repeat|verbatim|evidence|sources?|citations?|"
    r"explain|details?|detailed|steps?|list|examples?|paragraphs?|sentences?|"
    r"story|stories|poem|poetry|haiku|limerick|monologue|word[- ]for[- ]word)\b"
    r"|\bwhat (?:exactly )?did you say\b",
    re.IGNORECASE,
)

BRIEF_REPLY_GUIDANCE = (
    "\n\nThe previous attempt exceeded the ordinary conversational length. "
    "Answer the current message in one or two brief sentences, at most 45 words. "
    "Keep the specific emotional meaning: sincere warmth for good news, care for distress, "
    "a relevant comic turn for invited banter. Drop redundant acknowledgement and a generic "
    "closing offer if the specific care already says enough. Preserve supported facts, "
    "source attribution, meaningful uncertainty and recipient judgment. Do not add a joke "
    "to distress or invent circumstances. Do not explain this revision."
)


def needs_brief_reply(
    reply: str, messages: Sequence[ConversationMessage], target: str | None
) -> bool:
    """Recognize clear excess, preserving requested detail and literal references."""
    if (
        not target
        or requested_quotation(target)
        or _EXPANDED_REQUEST.search(target)
        or any(message.origin == "reference" for message in messages)
    ):
        return False
    return len(_WORD.findall(reply)) > 60 or sentence_count(reply) > 2


def sentence_count(reply: str) -> int:
    """Count prose boundaries without treating quoted punctuation as prose sentences."""
    text = _QUOTED.sub("quoted text", dialogue_content(reply)).strip()
    count = 0
    last_end = 0
    for end in _END.finditer(text):
        if end.group() == "..." or _ABBREVIATION.search(text[: end.end()]):
            continue
        if text[last_end : end.start()].strip():
            count += 1
        last_end = end.end()
    return count + bool(text[last_end:].strip())
