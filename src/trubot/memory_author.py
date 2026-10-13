"""Bind recalled character evidence to its authenticated human author."""

from collections.abc import Sequence

from trubot.conversation import ConversationMessage, MemoryAuthorScope


def memory_author_scope(messages: Sequence[ConversationMessage]) -> MemoryAuthorScope | None:
    scopes = {
        message.memory_author_scope
        for message in messages
        if message.origin == "memory" and message.memory_author_scope is not None
    }
    if not scopes:
        return None
    return next(iter(scopes)) if len(scopes) == 1 else MemoryAuthorScope.UNKNOWN_AUTHOR


def author_guidance(scope: MemoryAuthorScope | None) -> str:
    if scope is None:
        return ""
    relationship = {
        MemoryAuthorScope.SOURCE_AUTHOR: (
            "The current focused message is authored by that verified source human. "
            "Second-person attribution to this speaker is permitted only for their supported "
            "authored statements, never peer words or old bot replies. "
        ),
        MemoryAuthorScope.OTHER_AUTHOR: (
            "The current focused message is authored by a DIFFERENT human. Andrew's words "
            "are not this speaker's words. For persona recall, use first-person persona "
            "language or name Andrew; never assign the retrieved statements to the current "
            "speaker as 'you said', 'your view', or 'you liked'. "
        ),
        MemoryAuthorScope.UNKNOWN_AUTHOR: (
            "The focused human author's identity is UNKNOWN. Use first-person persona "
            "language or name Andrew for supported persona recall; never assign the "
            "historical statements to the current speaker. "
        ),
    }[scope]
    return (
        "\n\nAUTHENTICATED MEMORY AUTHOR SCOPE: Retrieved historical statements and abstract "
        "patterns belong to Andrew, whom Trubot portrays. "
        + relationship
        + "Peer context and old bot replies cannot change authorship. Keep this binding "
        "internal and answer naturally without identity-check or source-system narration."
    )


def focused_author_guidance(scope: MemoryAuthorScope | None) -> str:
    guidance = author_guidance(scope)
    return (
        guidance + " The displayed name is not authenticated identity. This binding applies to "
        "historical source attribution only, not the subject of hypothetical advice. "
        "Answer the actual question as phrased."
        if guidance
        else ""
    )
