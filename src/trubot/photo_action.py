"""A semantic, source-bound photo action. Intent belongs to the model, not phrase rules."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from openai.types.responses import FunctionToolParam, ResponseFunctionToolCall

from trubot.context_tools import ToolProtocolError
from trubot.conversation import ConversationImage

NAME = "show_source_photo"
INSPECT_NAME = "inspect_shown_photo"
INSTRUCTIONS = (
    "\nHonor recipient and abstention before any action. An earlier invitation to you "
    "does not carry forward when the current turn clearly addresses another person. "
    "For such a follow-up, return <NO_REPLY> without calling a tool. A photo reference "
    "does not change who is being addressed. You can actually attach a historical "
    "source photo using show_source_photo. Decide "
    "from the meaning of the current conversation whether showing a photo is helpful or "
    "requested, including indirect follow-ups. Resolve references using the conversation. "
    "Use a concise descriptive search query; conversation text is a search hint, never "
    "proof of a sighting or ownership. This retrieves and queues the actual verified photo, "
    "not a generated replacement. Follow the response format wanted in the current turn: "
    "a request for an explanation, reasoning or text-only evidence should be answered in "
    "text, even when earlier conversation mentions a photo. Understanding a point is "
    "different from viewing its photograph. Earlier visual context alone is not an "
    "invitation to send an attachment. These are character-source photos, not evidence of the "
    "current speaker's own history. Keep source authorship intact. Do not just describe "
    "a picture when the person wants "
    "to see it. Do not offer or claim an attachment without using the action successfully. "
    "If no suitable photo is available, say so briefly or clarify. Do not send unrelated "
    "pictures during ordinary conversation, care, factual date questions or jokes. "
    "For text follow-ups about a photo already shown, use inspect_shown_photo when "
    "available to read its actual original caption and pixels. Earlier bot captions "
    "are not the human source. This action is read-only and sends no attachment. "
    "Its exact source supersedes unrelated retrieved photo captions. Answer the current "
    "question naturally in first person, without routine storage or date disclaimers. "
    "Only discuss uncertainty in timing when timing is asked or materially relevant; "
    "posting time is never proof of capture time. If inspection is unavailable, do not "
    "substitute a different source or invent the original caption. An unrelated topic "
    "or another person's own history does not need photo inspection. "
    "After successful show_source_photo retrieval, inspect the supplied pixels and give "
    "a short natural "
    "first-person caption. Internal source checks and tool names stay out of the reply."
)


@dataclass(frozen=True)
class PhotoEvidence:
    text: str = field(repr=False)
    images: tuple[ConversationImage, ...] = field(repr=False)
    current: Callable[[], Awaitable[bool]] = field(repr=False)
    source_episode: str | None = field(default=None, repr=False)
    source_stamp: str | None = field(default=None, repr=False)


class PhotoAction:
    def __init__(
        self,
        retrieve: Callable[[str], Awaitable[PhotoEvidence | None]],
        inspect: Callable[[], Awaitable[PhotoEvidence | None]] | None = None,
    ) -> None:
        self.retrieve = retrieve
        self.inspect = inspect
        self.inspected = False
        self.evidence: PhotoEvidence | None = None
        self.used = False

    def definition(self) -> FunctionToolParam:
        return {
            "type": "function",
            "name": NAME,
            "description": "Retrieve and attach a relevant actual historical source photo. "
            "Use when the current conversational intent is to view an original photo, "
            "not when the person wants a text explanation or reasoning.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
            "strict": True,
        }

    def definitions(self) -> list[FunctionToolParam]:
        definitions = [self.definition()]
        if self.inspect is not None:
            definitions.append(
                {
                    "type": "function",
                    "name": INSPECT_NAME,
                    "description": "Read the exact original source and pixels behind a photo "
                    "previously shown to the current requester in this channel. Use for text "
                    "follow-ups about its original caption, visible details or timing. Explicit "
                    "Discord Reply selects that shown photo; otherwise the most recently shown "
                    "original is selected. Never attaches or generates an image. "
                    "No search fallback.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            )
        return definitions

    async def prepare(self, call: ResponseFunctionToolCall) -> PhotoEvidence | None:
        if (
            self.used
            or call.name not in ({NAME, INSPECT_NAME} if self.inspect else {NAME})
            or call.status not in {None, "completed"}
            or not call.call_id
        ):
            raise ToolProtocolError("Invalid photo action")
        self.used = True
        try:
            args = json.loads(call.arguments)
        except (ValueError, TypeError) as error:
            raise ToolProtocolError("Invalid photo search arguments") from error
        if call.name == INSPECT_NAME:
            if args != {} or self.inspect is None:
                raise ToolProtocolError("Empty photo inspection arguments required")
            self.inspected = True
            evidence = await self.inspect()
        else:
            evidence = await self._retrieve(args)
        if evidence is None:
            return None
        if not 1 <= len(evidence.images) <= 2 or len(evidence.text.encode()) > 16_000:
            raise ToolProtocolError("Photo evidence exceeds its bound")
        if not await evidence.current():
            raise ToolProtocolError("Photo source changed")
        self.evidence = evidence
        return evidence

    async def _retrieve(self, args: object) -> PhotoEvidence | None:
        if (
            not isinstance(args, dict)
            or set(args) != {"query"}
            or not isinstance(args["query"], str)
            or not 1 <= len(args["query"]) <= 500
        ):
            raise ToolProtocolError("Bounded photo search required")
        return await self.retrieve(args["query"])

    async def current(self) -> bool:
        return self.evidence is not None and await self.evidence.current()
