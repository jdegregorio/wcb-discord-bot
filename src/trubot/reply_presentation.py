"""Conservative dialogue framing for ordinary speech, preserving requested artifacts."""

from __future__ import annotations

import re

_LITERAL_REQUEST = re.compile(
    r"\b(?:quot(?:e|ing|ation)|repeat|verbatim|caption|word[- ]for[- ]word)\b"
    r"|\b(?:exact|original|full) (?:words|wording)\b"
    r"|\bwhat (?:exactly )?(?:did|do) you say\b",
    re.IGNORECASE,
)


def requested_quotation(target: str) -> bool:
    """Conservatively retain source wording and requested text artifacts."""
    return bool(_LITERAL_REQUEST.search(target))


def dialogue_content(text: str) -> str:
    """Unwrap one complete pair only; embedded or ambiguous quotes stay untouched."""
    text = text.strip()
    for opening, closing in (('"', '"'), ("“", "”")):
        if (
            len(text) >= 2
            and text.startswith(opening)
            and text.endswith(closing)
            and text.count(opening) == (2 if opening == closing else 1)
            and (opening == closing or text.count(closing) == 1)
        ):
            return text[1:-1].strip()
    return text


def ordinary_reply(text: str, target: str | None) -> str:
    if not target or requested_quotation(target):
        return text
    return dialogue_content(text)
