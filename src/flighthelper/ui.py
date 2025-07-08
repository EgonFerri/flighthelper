"""
UI – one-liner ChatInterface (messages mode) with API docs disabled
"""

import gradio as gr
from .agent import ask


def chat_fn(message: str, history: list[dict]) -> str:
    """Return the assistant’s reply; ChatInterface manages history."""
    return ask(message)


def launch() -> None:
    gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="✈️ Flight-Finder AI",
        description="Ask for cheap routes, date windows, stopovers…",
        # you can add `examples=[...]` here later if desired
    ).launch(
        server_name="0.0.0.0",   # avoids “localhost not accessible” check
        server_port=7860,
        share=False,             # set True if you need a public link
        show_api=False,          # ← disables the buggy OpenAPI generation
    )
