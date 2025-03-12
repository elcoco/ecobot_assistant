#!/usr/bin/env python

from typing import Optional
from pathlib import Path
import asyncio
from queue import Queue
import time

from core.wakeword import WakeWord
from core.tts import TTS
from core.stt import STT
from core.ai.ai import AI

from core.ai import tools


class App():
    def __init__(self) -> None:
        ...

    def speak(self, text: str, tts, ww):
        """ Returns True if interrupted by wakeword """
        with tts(text):
            while tts.is_speaking():
                if ww.is_triggered():
                    return True

    def conversation_mode(self):
        messages = []

        while True:
            with tts("listening"):
                tts.wait()
                
            # Blocking call
            text = ". ".join(stt.listen())

            try:
                with ww, ai(text):
                    while not ai.is_finished():
                        if not (sentence := ai.get_sentence()):
                            time.sleep(.1)
                            continue

                        if self.speak(sentence, tts, ww):
                            break

            except KeyboardInterrupt:
                break
        ...

    def run(self):

        #stt = STT(Path("assets/stt_models/vosk-model-en-us-0.22"))
        stt = STT(Path("assets/stt_models/vosk-model-small-en-us-0.15"))

        #tts = TTS(Path("assets/tts_models/en_US-amy-low.onnx"))
        tts = TTS(Path("assets/tts_models/en_US-lessac-medium.onnx"))
        #tts = TTS(Path("assets/tts_models/en_US-lessac-high.onnx"))

        ai = AI()

        while True:
            ww = WakeWord(Path("assets/ww_models/hey_jarvis_v0.1.onnx"), "hey_jarvis_v0.1")

            print("Ready...")

            try:
                with ww:
                    ww.wait()
            except KeyboardInterrupt:
                print("exit by interrupt")
                break

            with tts("listening"):
                tts.wait()
                
            # Blocking call
            text = ". ".join(stt.listen())

            try:
                with ww, ai(text, tools):
                    while not ai.is_finished():
                        if not (sentence := ai.get_sentence()):
                            time.sleep(.1)
                            continue

                        if self.speak(sentence, tts, ww):
                            break

            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    app = App()
    app.run()
