#!/usr/bin/env python

from typing import Optional
from pathlib import Path
import asyncio
from queue import Queue
import time

from core.ai.ai import pre_match_tools

from core.ai.tools.base import ToolBaseClass, ToolError
from core import tts, stt, ww, tools


# TODO: add words like kodi and toggle to vosk vocabulary so it will bias towards these words

class App():
    def run(self):

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

                tool.call(query)

            except KeyboardInterrupt:
                print("exit by interrupt")
                break
            except ToolError as e:
                print(e)


if __name__ == "__main__":
    app = App()
    app.run()
