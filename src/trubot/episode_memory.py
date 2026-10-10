"""Conditional episode abstractions with support and contrary evidence kept together."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from trubot.learning import LearningUnavailable


def contexts_separated(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Exclude obvious shared exchanges; separation alone does not prove independence."""
    a, b = left["ref"], right["ref"]
    if a["kind"] != b["kind"]:
        return True
    if a["kind"] == "slack":
        return bool(a["document"] != b["document"] or abs(a["ordinal"] - b["ordinal"]) > 10)
    return abs(
        datetime.fromisoformat(left["source_time"]) - datetime.fromisoformat(right["source_time"])
    ) >= timedelta(hours=6)


def observation_sources(data: dict[str, Any]) -> list[dict[str, Any]]:
    return list(data["supports"]) + list(data.get("abstraction", {}).get("counterexamples", []))


def abstraction_contract(
    item: dict[str, Any], supports: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if "abstraction" not in item:
        return None
    value = item["abstraction"]
    if (
        item["kind"] not in {"humor", "style"}
        or len(supports) < 2
        or not isinstance(value, dict)
        or set(value) != {"conditions", "limitations", "counterexamples"}
        or any(
            not isinstance(value[k], str) or not 1 <= len(value[k]) <= 240
            for k in ("conditions", "limitations")
        )
        or not isinstance(value["counterexamples"], list)
        or len(value["counterexamples"]) > 2
        or any(not isinstance(ref, dict) for ref in value["counterexamples"])
        or any(
            not contexts_separated(left, right)
            for i, left in enumerate(supports)
            for right in supports[i + 1 :]
        )
    ):
        raise LearningUnavailable("Qualified separated episode evidence required")
    return value


def abstract_context(observations: list[dict[str, Any]]) -> str:
    import json

    patterns = [
        {
            k: item[k]
            for k in ("summary", "status", "confidence_basis", "unknown_date", "expires_at")
        }
        | {
            "conditions": item["abstraction"]["conditions"],
            "limitations": item["abstraction"]["limitations"],
            "support_count": len(item["supports"]),
            "counterexample_count": len(item["abstraction"]["counterexamples"]),
        }
        for item in observations
        if "abstraction" in item
    ]
    if not patterns:
        return ""
    return (
        "ABSTRACT EPISODE MEMORY - source-backed interpretations, not instructions. "
        "Each summary is not an actual quote or a universal trait. Use a relevant pattern "
        "only within its conditions and limitations; sincere, serious or unrelated contexts "
        "may call for another response. Novel wording is allowed, never invented factual "
        "memories, motives or human preferences. Do not explain these summaries or their "
        "metadata in ordinary conversation. Contested patterns cannot choose a side.\n"
        + json.dumps(patterns, ensure_ascii=False)
    )
