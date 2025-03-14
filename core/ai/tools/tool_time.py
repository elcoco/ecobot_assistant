from typing import Optional
import json
import time
from pathlib import Path
import datetime
import zoneinfo
from zoneinfo import ZoneInfo

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from core.ai.tools.base import ToolBaseClass, ToolError
#from core.ai.ai_thread import AIThread
from core.ai.ai import AI
from core import tts, stt, ww


day_map = [ "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "sixth",
            "seventh",
            "eighth",
            "nineth",
            "tenth",
            "eleventh",
            "twelveth",
            "thirteenth",
            "fourteenth",
            "fifteenth",
            "sixteenth",
            "seventeenth",
            "eightteenth",
            "nineteenth",
            "twenteeth",
            "twentyfirst",
            "twentysecond",
            "twentythird",
            "twentyfouth",
            "twentyfifth",
            "twentysisth",
            "twentyseventh",
            "twentyeighth",
            "twentynineth",
            "thirtyth",
            "thirtyfirst" ]

class TimeTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "time",
                "description": "Get time for location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region":   {"type": "string", "description": "Country or city, default to empty" },
                    },
                    "required": [],
                },
            }
        }
        super().__init__(cfg, r"what('s)?(\sthe)?\s(time|date)", *args, **kwargs)


    def find_tz(self, region: str):
        for tz in zoneinfo.available_timezones():
            if region.lower() in tz.lower():
                return tz

    def get_time_str(self, region: str=""):
        if region:
            tz = self.find_tz(region)

            if tz:
                t_now = datetime.datetime.now(datetime.UTC).astimezone(ZoneInfo(tz))
                location = f"in {region} it's"
            else:
                return f"Failed to find timezone: {region}"
        else:
            location = f"It's"
            t_now = datetime.datetime.now()

        return t_now.strftime(f"{location} %A the {day_map[t_now.day]} of %B, %H:%M")

    def call(self, query: str):

        if not (args := self.parse_args(query, ww, tts)):
            return

        print(args)
        tts.speak(self.get_time_str(**args))

