from typing import Optional
import re
from pathlib import Path

from ollama import Client

from core.tts import TTS
from core.wakeword import WakeWord
from core.ai.ai import AI


class ToolError(Exception):
    ...

class ToolBaseClass():
    def __init__(self, cfg: dict, pre_match: str, ai_model: str, skip_ai: bool=False):
        self._config = cfg

        # Pre match checks request against given reggex
        self._pattern = re.compile(pre_match)
        self._ai_model = ai_model

    @property
    def name(self):
        return self._config["function"]["name"]

    def get_cfg(self):
        return self._config

    def pre_match(self, text):
        """ Check patern against the query so that we can see what tool to use """
        if self._pattern:
            return re.match(self._pattern, text)

        return True

    def parse_args(self, query: str, ww: WakeWord, tts: TTS) -> str:
        """ Parse query into arguments """
        ai = AI(self._ai_model)
        with ww, ai(query, tools=[self.get_cfg()]) as t:
            while not t.is_finished():
                if ww.is_triggered():
                    return

        if not (args := t.get_args()):
            tts.speak(f"{self.name} tool failed to run!")
            raise ToolError("Tool failed to run!")

        return args

    def call(self, *args, **kwargs):
        """ Needs to be implemented when subclassing """

