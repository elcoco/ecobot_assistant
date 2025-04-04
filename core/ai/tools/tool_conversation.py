from typing import Optional
import json
import time
from pathlib import Path
import re

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from core.ai.tools.base import ToolBaseClass, ToolError
#from core.ai.ai_thread import AIThread
from core.ai.ai import AI

from core import tts, stt, ww


class ConversationTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "conversation",
                "description": "Start a conversation",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
        }
        super().__init__(cfg, r"^start\sconversation", *args, **kwargs)

    def call(self, query: str):
        tts.speak("What can I help you with?")
        context = []

        while True:
            text = []
            query = ". ".join(stt.listen())

            if re.match(r"^stop.*$", query.lower()):
                tts.speak("Ending conversation.")
                break
            elif not query:
                continue


            # Lookup ai and feed chunks of text to TTS while being interruptable by wakeword
            ai = AI(self._ai_model)
            with ww, ai(query, context=context) as t:
                while not t.is_finished():
                    if ww.is_triggered():
                        break

                    if not (sentence := t.get_sentence()):
                        time.sleep(.1)
                        continue

                    text.append(sentence)

                    with tts(sentence):
                        if tts.wait(ww.is_triggered):
                            break

                context.append({ "role": "user", "content": query })
                context.append({"role": "assistant", "content": ".\n".join(text)})
