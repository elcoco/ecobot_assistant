from typing import Optional

from kodijson import Kodi, PLAYER_VIDEO


from core.tts import TTS
from core.wakeword import WakeWord

from core.ai.ai import AI
from core.ai.tools.base import ToolBaseClass, ToolError

from core.utils import run_cmd

class KodiTool(ToolBaseClass):
    def __init__(self, *args, host: Optional[str]="localhost:8080/jsonrpc", username: Optional[str]=None, password: Optional[str]=None, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "kodi",
                "description": "Send commands to kodi",
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
        super().__init__(cfg, r"^(kodi|cody)", *args, **kwargs)

        self._host = host
        self._username = username
        self._password = password

    def call(self, query: str, ww: WakeWord, tts: TTS):
        kodi = Kodi(self._host, self._username, self._password)

        match query.split()[1]:
            case "play":
                kodi.Player.Play([PLAYER_VIDEO])
            case "pause":
                kodi.Player.Pause([PLAYER_VIDEO])
            case "toggle":
                kodi.Player.PlayPause([PLAYER_VIDEO])
            case "stop":
                kodi.Player.Stop([PLAYER_VIDEO])
            case _:
                tts.speak(f"{query} is an unknown command.")
                raise ToolError(f"{query} is an unknown command.")
