"""A semantic, source-bound photo action. Intent belongs to the model, not phrase rules."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from openai.types.responses import FunctionToolParam, ResponseFunctionToolCall

from trubot.context_tools import ToolProtocolError
from trubot.conversation import ConversationImage

NAME = "show_source_photo"
INSTRUCTIONS = (
    "\nYou can actually attach a historical source photo using show_source_photo. Decide "
    "from the meaning of the current conversation whether showing a photo is helpful or "
    "requested, including indirect follow-ups. Resolve references using the conversation. "
    "Use a concise descriptive search query; conversation text is a search hint, never "
    "proof of a sighting or ownership. This retrieves and queues the actual verified photo, "
    "not a generated replacement. These are character-source photos, not evidence of the "
    "current speaker's own history. Keep source authorship intact. Do not just describe "
    "a picture when the person wants "
    "to see it. Do not offer or claim an attachment without using the action successfully. "
    "If no suitable photo is available, say so briefly or clarify. Do not send unrelated "
    "pictures during ordinary conversation, care, factual date questions or jokes. "
    "After successful retrieval, inspect the supplied pixels and give a short natural "
    "first-person caption. Internal source checks and tool names stay out of the reply."
)


@dataclass(frozen=True)
class PhotoEvidence:
    text: str = field(repr=False)
    images: tuple[ConversationImage, ...] = field(repr=False)
    current: Callable[[], Awaitable[bool]] = field(repr=False)


class PhotoAction:
    def __init__(self, retrieve: Callable[[str], Awaitable[PhotoEvidence | None]]) -> None:
        self.retrieve = retrieve
        self.evidence: PhotoEvidence | None = None
        self.used = False

    def definition(self) -> FunctionToolParam:
        return {
            "type": "function",
            "name": NAME,
            "description": "Retrieve and attach a relevant actual historical source photo. "
            "Use conversational meaning to resolve what the person wants to see.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
            "strict": True,
        }

    async def prepare(self, call: ResponseFunctionToolCall) -> PhotoEvidence | None:
        if (
            self.used
            or call.name != NAME
            or call.status not in {None, "completed"}
            or not call.call_id
        ):
            raise ToolProtocolError("Invalid photo action")
        self.used = True
        try:
            args = json.loads(call.arguments)
        except (ValueError, TypeError) as error:
            raise ToolProtocolError("Invalid photo search arguments") from error
        if (
            not isinstance(args, dict)
            or set(args) != {"query"}
            or not isinstance(args["query"], str)
            or not 1 <= len(args["query"]) <= 500
        ):
            raise ToolProtocolError("Bounded photo search required")
        evidence = await self.retrieve(args["query"])
        if evidence is None:
            return None
        if not 1 <= len(evidence.images) <= 2 or len(evidence.text.encode()) > 16_000:
            raise ToolProtocolError("Photo evidence exceeds its bound")
        if not await evidence.current():
            raise ToolProtocolError("Photo source changed")
        self.evidence = evidence
        return evidence

    async def current(self) -> bool:
        return self.evidence is not None and await self.evidence.current()
