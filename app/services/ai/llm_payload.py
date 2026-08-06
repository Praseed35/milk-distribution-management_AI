import json
from datetime import date
from typing import Any

PII_KEYS = {"primary_phone", "alternate_phone", "address", "email"}

OUT_OF_SCOPE_INSTRUCTION = (
    'If the question cannot be answered from the provided data, '
    'respond exactly: "I cannot answer that from the available data".'
)


def strip_sensitive_fields(value: Any) -> Any:
    """Recursively remove customer contact fields from any structure."""
    if isinstance(value, dict):
        return {
            k: strip_sensitive_fields(v)
            for k, v in value.items()
            if k not in PII_KEYS
        }
    if isinstance(value, list):
        return [strip_sensitive_fields(v) for v in value]
    if isinstance(value, tuple):
        return [strip_sensitive_fields(v) for v in value]
    return value


def _system_prompt(data_range: tuple[date, date]) -> str:
    return (
        "You are a business analyst for a milk distribution company. "
        "Answer only from the data provided. Always state the data range you "
        "are covering in your answer. "
        f"Data range covered: {data_range[0]} to {data_range[1]}. "
        + OUT_OF_SCOPE_INSTRUCTION
    )


def build_insights_context(
    context: dict,
    data_range: tuple[date, date],
) -> list[dict]:
    payload = strip_sensitive_fields(context)
    return [
        {
            "role": "system",
            "content": _system_prompt(data_range),
        },
        {
            "role": "user",
            "content": (
                "Write a brief plain-language business summary covering today's "
                "operations, revenue trend, top-performing routes, notable "
                "increases or declines, and any flagged items. Use only the "
                "data below.\n\n"
                + json.dumps(payload, default=str)
            ),
        },
    ]


def build_chat_context(
    context: dict,
    data_range: tuple[date, date],
    question: str,
    history: list[dict] | None = None,
) -> list[dict]:
    payload = strip_sensitive_fields(context)
    messages: list[dict] = [
        {
            "role": "system",
            "content": _system_prompt(data_range),
        }
    ]
    for turn in (history or [])[-8:]:
        messages.append({
            "role": "user" if turn.get("role") == "user" else "assistant",
            "content": str(turn.get("content", "")),
        })
    messages.append({
        "role": "user",
        "content": (
            f"Question: {question}\n\n"
            "Use only the aggregated business data below to answer.\n\n"
            + json.dumps(payload, default=str)
        ),
    })
    return messages
