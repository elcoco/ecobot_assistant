from typing import Optional

from core.ai.tools.base import ToolBaseClass, ToolError

from core.ai.ai import AI


class TimerTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "timer",
                "description": "Set a simple timer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seconds": {"type": "int", "description": "The amount in seconds" },
                        "minutes": {"type": "int", "description": "The amount in minutes" },
                        "hours": {"type": "int", "description": "The amount in hours" },
                    },
                    "required": ["seconds", "minutes"],
                },
            }
        }
        super().__init__(cfg, r"^set\s(?:[a-z]*\s)time", *args, **kwargs)

    def get_time_str(self, seconds: int) -> str:
        hours = int(seconds / (60*60))
        rest = seconds % (60*60)
        minutes = int(rest / (60))
        seconds = rest % int((60))

        ret = []
        if hours:
            ret.append(f"{hours} hours")
        if minutes:
            ret.append(f"{minutes} minutes")
        if seconds:
            ret.append(f"{seconds} seconds")

        return " and ".join(ret)

    def get_result(self, seconds: Optional[str]=None, minutes: Optional[str]=None, hours: Optional[str]=None) -> str:
        try:
            sec: int = 0
            if seconds:
                sec += int(seconds)
            if minutes:
                sec += int(float(minutes) * 60)
            if hours:
                sec += int(float(hours) * (60 * 60))
        except ValueError:
            raise ToolError(f"I expected a number in seconds but I received {seconds}, {minutes}, {hours}")

        return f"Setting a timer for {self.get_time_str(sec)}."


    def call(self, query: str):
        if args := self.parse_args(query, ww, tts):
            result = self.get_result(**args)
            tts.speak(f"{result}")
