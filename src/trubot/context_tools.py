"""Selected, read-only capabilities with one explicit execution boundary per reply."""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from typing import Protocol

from openai.types.responses import FunctionToolParam, ResponseFunctionToolCall

from trubot.conversation import ReplyMode

logger = logging.getLogger(__name__)
MAX_TOOL_OUTPUT_BYTES = 6_000


class ContextSkill(Protocol):
    name: str
    instructions: str

    def applies(self, target: str, mode: ReplyMode) -> bool: ...

    def definition(self) -> FunctionToolParam: ...

    async def read(self) -> dict[str, object]: ...


class ToolProtocolError(ValueError):
    """An unapproved or incomplete tool request must never be executed or posted."""


class ContextTools:
    def __init__(self, skills: Sequence[ContextSkill] = ()) -> None:
        self._skills = tuple(skills)
        if len({skill.name for skill in skills}) != len(skills):
            raise ValueError("Context skill names must be unique")

    def select(self, target: str | None, mode: ReplyMode) -> tuple[ContextSkill, ...]:
        return tuple(skill for skill in self._skills if target and skill.applies(target, mode))

    async def execute(
        self, calls: Sequence[ResponseFunctionToolCall], selected: Sequence[ContextSkill]
    ) -> str:
        # Validate the entire batch before any I/O. No partial execution of a bad batch.
        if len(calls) != 1:
            raise ToolProtocolError("Exactly one selected context call permitted")
        call = calls[0]
        skill = next((s for s in selected if s.name == call.name), None)
        if skill is None or call.status not in {None, "completed"} or not call.call_id:
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
