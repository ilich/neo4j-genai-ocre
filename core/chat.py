import asyncio
import inspect
import textwrap
from abc import ABC, abstractmethod

import ipywidgets as widgets
import nest_asyncio
from IPython.display import display
from neo4j_graphrag.types import LLMMessage

TERMINAL_LINE_WIDTH = 80


class ChatService(ABC):
    @abstractmethod
    def chat(self, query: str, history: list[LLMMessage]) -> str:
        pass

    def clear(self):
        pass


def run(chat: ChatService) -> str:
    history = []

    output = widgets.Output()

    text_field = widgets.Textarea(
        value="", placeholder="Ask anything...", disabled=False
    )

    send_button = widgets.Button(
        description="Send", button_style="", tooltip="Send message", icon="comment"
    )

    def on_send_click(b):
        with output:
            question = text_field.value.strip()
            print(f">>> You: {question}")
            if not question:
                print(">>> Please enter a question.")
                return

            text_field.value = ""

            # Support both sync and async chat implementations
            chat_method = getattr(chat, "chat")
            if inspect.iscoroutinefunction(chat_method):
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                answer = loop.run_until_complete(chat.chat(question, history))
            else:
                answer = chat.chat(question, history)
            print(textwrap.fill(f"<<< Assistant: {answer}", width=TERMINAL_LINE_WIDTH))
            print()

            history.append(LLMMessage(role="user", content=question))
            history.append(LLMMessage(role="assistant", content=answer))

    clear_button = widgets.Button(
        description="Clear",
        button_style="warning",
        tooltip="Start new session",
        icon="archive",
    )

    def on_clear_click(b):
        chat.clear()
        text_field.value = ""
        history.clear()
        output.clear_output()

    send_button.on_click(on_send_click)
    clear_button.on_click(on_clear_click)

    button_box = widgets.HBox([send_button, clear_button])
    display(text_field, button_box, output)
