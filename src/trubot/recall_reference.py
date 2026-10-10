"""Resolve quotation lookup keys without making conversation text personal evidence."""

from __future__ import annotations

import re
from collections.abc import Sequence

from trubot.conversation import ConversationMessage
from trubot.memory import RecallPresentation, quotation_key, recall_presentation

_QUOTES = re.compile(r'“([^”]*)”|"([^"]*)"')
_REFERENCE = re.compile(r"\b(?:that|this|it)\b", re.IGNORECASE)
_ELLIPTICAL = re.compile(
    r"(?:what|which) (?:(?:exact|specific|precise|calendar) )?"
    r"(?:day|date|month|year|source|evidence)|(?:exactly )?when",
    re.IGNORECASE,
)


def _quotation(text: str) -> str | None:
    quotes: list[str] = [left or right for left, right in _QUOTES.findall(text[:8000])]
    if not quotes:
        return "" if any(mark in text for mark in ('"', "“", "”")) else None
    unique = {quotation_key(quote): quote for quote in quotes}
    if len(unique) != 1 or any(not 8 <= len(quote) <= 500 for quote in quotes):
        return ""
    return next(iter(unique.values()))


def _referential(text: str) -> bool:
    return bool(_REFERENCE.search(text) or _ELLIPTICAL.fullmatch(text.strip().rstrip("?!. ")))


def recall_quotation(request: str, history: Sequence[ConversationMessage]) -> str | None:
    """None means topical search, empty means unresolved, otherwise an exact lookup key.

    Only a focused timing/evidence request can initiate lookup. An explicit current
    quote wins. Implicit lookup crosses only timing/evidence follow-ups, never a
    newer subject or a peer's quotation. Every key still needs current human support.
    """
    if recall_presentation(request) is RecallPresentation.CONTENT:
        return None
    explicit = _quotation(request)
    if explicit is not None:
        return explicit
    # A named focused topic supersedes implicit conversation continuity.
    if re.search(r"\b(?:about|regarding)\s+(?!(?:that|this|it)\b)\S", request, re.IGNORECASE):
        return None
    if not _referential(request):
        return None
    recent = list(history[-8:])
    # A visual focus may already be included in the history before memory is added.
    if recent and recent[-1].role == "user" and recent[-1].content.split(": ", 1)[-1] == request:
        recent.pop()
    while recent:
        reply = recent.pop()
        if reply.role != "assistant":
            return ""
        quote = _quotation(reply.content)
        if quote is not None:
            return quote
        if not recent or recent[-1].role != "user":
            return ""
        question = recent.pop().content.split(": ", 1)[-1]
        if recall_presentation(question) is RecallPresentation.CONTENT:
            return ""
        explicit = _quotation(question)
        if explicit is not None:
            return explicit
        if not _referential(question):
            return ""
    return ""


def quotation_unavailable() -> str:
    return (
        "QUOTATION RECALL - the focused reference has no matching current attributed source "
        "or is ambiguous. Earlier bot quotations cannot substitute for it. "
        "Do not invent a quotation, event or date. Respond briefly and naturally; "
        "ask which quotation only if needed. Keep lookup mechanics internal."
    )
