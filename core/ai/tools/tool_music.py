from typing import Optional

from core.ai.tools.base import ToolBaseClass, ToolError

from core.tts import TTS
from core.wakeword import WakeWord

from core.utils import run_cmd

class MusicTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "play_music",
                "description": "play media by given song or video name and optionally artist name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name":   {"type": "string", "description": "the song or movie name" },
                        "application":   {"type": "string", "description": "the name of the application where the music should be played" },
                        "artist": {"type": "string", "description": "the artist or directors name" },
                    },
                    "required": ["name", "application"],
                },
            }
        }
        super().__init__(cfg, r"^play ", *args, **kwargs)

    def call(self, name: str, application: str, artist: Optional[str]=None) -> str:
        ret = f"Playing: {name}"
        if artist:
            ret += f" by {artist}"
        if application:
            ret += f" on {application}"
        return ret


class MediaControlTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "control_media",
                "description": "Start, pause or stop playback",
                "parameters": {
                    "type": "object",
                    "properties": { 
                        "command": {"type": "string", "description": "The command given to the media player" },
                    },
                    "required": ["command"],
                },
            }
        }
        super().__init__(cfg, r"^(pause|start|toggle|stop)\s(play|plane|plain)", *args, skip_ai=True, **kwargs)

    def call(self, query: str, ww: WakeWord, tts: TTS):
        match query.split()[0]:
            case "start":
                command = "play"
            case "pause":
                command = "pause"
            case "toggle":
                command = "play-pause"
            case "stop":
                command = "stop"
            case _:
                tts.speak("{query} is an unknown command.")
                raise ToolError(f"{query} is an unknown command.")

        try:
            run_cmd(["playerctl", command])
        except OSError as e:
            tts.speak(f"Failed to execute command '{command}'. Is player c t l installed?")
            raise ToolError(f"Failed to execute command '{command}', I received error: {e}")
