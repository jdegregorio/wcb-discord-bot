"""Selected, read-only capabilities with one explicit execution boundary per reply."""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from typing import Protocol

from openai.types.responses import FunctionToolParam, ResponseFunctionToolCall

from trubot.context_focus import location_question
from trubot.conversation import ConversationMessage, ReplyMode

logger = logging.getLogger(__name__)
MAX_TOOL_OUTPUT_BYTES = 6_000


class ContextSkill(Protocol):
    name: str
    instructions: str

    def applies(self, target: str, mode: ReplyMode) -> bool: ...

    def definition(self) -> FunctionToolParam | None: ...

    async def read(self) -> dict[str, object]: ...


class ToolProtocolError(ValueError):
    """An unapproved or incomplete tool request must never be executed or posted."""


class ContextTools:
    def __init__(self, skills: Sequence[ContextSkill] = ()) -> None:
        self._skills = tuple(skills)
        if len({skill.name for skill in skills}) != len(skills):
            raise ValueError("Context skill names must be unique")

    def select(
        self,
        target: str | None,
        mode: ReplyMode,
        *,
        messages: Sequence[ConversationMessage] = (),
        requester_user_id: int | None = None,
    ) -> tuple[ContextSkill, ...]:
        selected = tuple(skill for skill in self._skills if target and skill.applies(target, mode))
        if selected:
            return selected
        resolved = location_question(
            target, messages, mode=mode, requester_user_id=requester_user_id
        )
        if resolved is None:
            return ()
        # An unlocated last-night question may acquire its explicitly supplied
        # location. Already located questions and other capabilities do not carry.
        question = resolved.rsplit(" Location: ", 1)[0]
        public = [
            skill
            for skill in self._skills
            if skill.name in {"get_up_last_night", "clarify_up_night_location"}
        ]
        prior = [skill for skill in public if skill.applies(question, mode)]
        candidates = [skill for skill in public if skill.applies(resolved, mode)]
        if (
            len(prior) != 1
            or prior[0].name != "clarify_up_night_location"
            or len(candidates) != 1
            or candidates[0].name != "get_up_last_night"
            or candidates[0].definition() is None
        ):
            return ()
        return tuple(candidates)

    async def execute(
        self, calls: Sequence[ResponseFunctionToolCall], selected: Sequence[ContextSkill]
    ) -> str:
        # Validate the entire batch before any I/O. No partial execution of a bad batch.
        if len(calls) != 1:
            raise ToolProtocolError("Exactly one selected context call permitted")
        call = calls[0]
        skill = next((s for s in selected if s.name == call.name), None)
        if (
            skill is None
            or skill.definition() is None
            or call.status not in {None, "completed"}
            or not call.call_id
        ):
            raise ToolProtocolError("Unapproved or incomplete context call")
        try:
            arguments = json.loads(call.arguments)
        except (ValueError, TypeError) as error:
            raise ToolProtocolError("Invalid context arguments") from error
        if arguments != {}:
            raise ToolProtocolError("Context calls accept no external parameters")
        logger.info("Executing read-only context skill name=%s", skill.name)
        output = json.dumps(await skill.read(), ensure_ascii=False, allow_nan=False)
        if len(output.encode()) > MAX_TOOL_OUTPUT_BYTES:
            raise ToolProtocolError("Context output exceeds its bound")
        return output
