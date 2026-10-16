"""Focused rolling recall windows, independent of source text and bot history."""

import re
from datetime import timedelta

_AUTHORED = re.compile(
    r"\b(?:say|said|saying|talked|talking|mentioned|messages?|conversations?|exchanges?|recall|remember|quote)\b",
    re.IGNORECASE,
)
# A narrow factual question, not a mention of an activity inside advice, a quote
# or an imagined choice. This supplies routing only, never personal evidence.
_ACTIVITY_QUESTION = re.compile(
    r"^(?:(?:where|what|which|how|when) )?"
    r"(?:have|has|did|were|was) (?P<subject>you|i|andrew|tru|trubot) "
    r"(?:(?:actually|really|ever|recently|just) ){0,2}"
    r"(?:(?:been )?(?:doing|reading|watching|playing|traveling|travelling|hiking|camping)"
    r"|travel|traveled|travelled|visit|visited|go|gone|went|vacation|vacationed"
    r"|hike|hiked|camp|camped|read|watch|watched|play|played|do|done"
    r"|been (?:anywhere|on (?:a |any )?trips?)|(?:take|taken|took) (?:a |any )?trips?)\b",
    re.IGNORECASE,
)


def activity_recall_subject(request: str) -> str | None:
    """Recognize an explicit personal activity question without resolving identities."""
    text = " ".join(request[:8000].casefold().removeprefix("🤖").strip().split())
    text = text.removeprefix("@trubot ")
    match = _ACTIVITY_QUESTION.match(text)
    return match["subject"] if match else None


_ROLLING = re.compile(
    r"\b(?:past|last)\s+(?:(?P<count>\d+|[a-z]+"
    r"(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?)\s+)?"
    r"(?P<unit>hours?|days?|weeks?)\b",
    re.IGNORECASE,
)
_COUNTS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
}

# Retrieval words only, not persona aliases or established interests.
WINDOW_WORDS = frozenset((*_COUNTS, "hour", "hours", "during", "over", "within"))


def recall_window(request: str) -> timedelta | None:
    """Return a rolling duration for authored recall, or None for another task.

    Unknown/zero quantities fail closed with an empty interval. Calendar dates,
    named months and current sports questions keep their existing route. The
    caller intersects a recognized duration with the authoritative retention floor.
    """
    request = request[:8000]
    if not _AUTHORED.search(request) and activity_recall_subject(request) is None:
        return None
    match = _ROLLING.search(request)
    dated_request = request[: match.start()] + request[match.end() :] if match else request
    if re.search(r"(?<!\d)(?:19|20)\d{2}(?!\d)", dated_request):
        return None
    if match:
        count = (match["count"] or "one").casefold()
        if count.isdecimal():
            # Avoid huge integer conversion or timedelta overflow from untrusted input.
            amount = min(int(count), 8760) if len(count) <= 9 else 8760
        else:
            parts = count.replace("-", " ").split()
            amount = _COUNTS.get(count, 0)
            if len(parts) == 2 and parts[0] in {"twenty", "thirty"}:
                amount = _COUNTS[parts[0]] + _COUNTS.get(parts[1], 0)
        multiplier = (
            1
            if match["unit"].casefold().startswith("hour")
            else (24 if match["unit"].casefold().startswith("day") else 168)
        )
        return timedelta(hours=min(amount * multiplier, 8760))
    if re.search(r"\b(?:recent|recently|latest|lately)\b", request, re.IGNORECASE):
        return timedelta(days=14)
    return None
