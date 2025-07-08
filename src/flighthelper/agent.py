"""
Agent – Chat Completions + Function Calling
Compatible with openai ≥ 1.93.0
"""

from __future__ import annotations

import json
from typing import Dict, List

from openai import OpenAI
from .config import OPENAI_KEY, GPT_MODEL, search_flights

client = OpenAI(api_key=OPENAI_KEY)

# ────────────────────────────────────────────────────────────────────────────
# Tool schema (NEW: wrapped in {"function": …})
# ────────────────────────────────────────────────────────────────────────────
flight_tool = {
    "type": "function",
    "function": {                               # ← required wrapper
        "name": "flight_search",
        "description": "Search live prices via the configured provider.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin":        {"type": "string"},
                "destination":   {"type": "string"},
                "depart_after":  {"type": "string", "format": "date"},
                "arrive_before": {"type": "string", "format": "date"},
                "limit":         {"type": "integer", "default": 8},
            },
            "required": [
                "origin",
                "destination",
                "depart_after",
                "arrive_before",
            ],
        },
    },
}

SYSTEM_PROMPT = (
    "You are a cost-savvy travel-planning analyst. "
    "When giving itineraries, include the booking deeplink."
)

# ────────────────────────────────────────────────────────────────────────────
# Helper to call the provider
# ────────────────────────────────────────────────────────────────────────────
def _run_flight_search(call) -> str:
    args = json.loads(call.function.arguments)
    results: List[Dict] = search_flights(
        origin=args["origin"],
        dest=args["destination"],
        depart_after=args["depart_after"],
        arrive_before=args["arrive_before"],
        limit=args.get("limit", 8),
    )
    return json.dumps(results, ensure_ascii=False)

# ────────────────────────────────────────────────────────────────────────────
# Public entry point
# ────────────────────────────────────────────────────────────────────────────
def ask(question: str) -> str:
    """
    user prompt → (optional) function call → final answer
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": question},
    ]

    # 1️⃣ First request: let the model decide if it needs the tool
    first = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        tools=[flight_tool],
        tool_choice="auto",
    ).choices[0]

    if first.finish_reason == "tool_calls":
        call = first.message.tool_calls[0]          # we only have one tool
        tool_result = _run_flight_search(call)

        # Append assistant stub + tool message
        messages.extend(
            [
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [call],
                },
                {
                    "role": "tool",
                    "tool_call_id": call.id,        # must echo id
                    "name": call.function.name,
                    "content": tool_result,
                },
            ]
        )

        # 2️⃣ Second request: model crafts the user-visible answer
        final = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
        ).choices[0]

        return final.message.content.strip()

    # No function call was needed
    return first.message.content.strip()
