#!/usr/bin/env python

from typing import Optional
from pathlib import Path
import asyncio
from queue import Queue
import time

from core.wakeword import WakeWord
from core.tts import TTS
from core.stt import STT
from core.ai.ai import pre_match_tools

from core.ai.tools.base import ToolBaseClass, ToolError
from core.ai.tools.tool_calculate import CalcTool
from core.ai.tools.tool_convert import ConvertTool
from core.ai.tools.tool_music import MusicTool, MediaControlTool
from core.ai.tools.tool_timer import TimerTool
from core.ai.tools.tool_lookup import LookupNewsTool

ai_model = "llama3.2"
tools: list[ToolBaseClass] = [ LookupNewsTool(ai_model),
                               MediaControlTool(ai_model),
                               ConvertTool(ai_model),
                               TimerTool(ai_model) ]

class App():
    def __init__(self) -> None:
        ...

    def speak(self, text: str, tts, ww):
        """ Returns True if interrupted by wakeword """
        with tts(text):
            while tts.is_speaking():
                if ww.is_triggered():
                    return True

    def run(self):

        stt = STT(Path("assets/stt_models/vosk-model-small-en-us-0.15"))
        tts = TTS(Path("assets/tts_models/en_US-lessac-medium.onnx"))
        ww = WakeWord(Path("assets/ww_models/hey_jarvis_v0.1.onnx"), "hey_jarvis_v0.1")

        while True:

            print("Waiting for wakeword...")

            try:
                ww.wait()
            except KeyboardInterrupt:
                print("exit by interrupt")
                break

            try:
                tts.speak("listening")
                    
                # Blocking call
                query = ". ".join(stt.listen())

                if not (tool := next(pre_match_tools(tools, query), None)):
                    tts.speak("No tool found to handle your request")
                    continue

                tool.call(query, ww, tts)

            except KeyboardInterrupt:
                print("exit by interrupt")
                break
            except ToolError as e:
                print(e)


if __name__ == "__main__":
    app = App()
    app.run()
