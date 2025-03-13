#!/usr/bin/env python3

from pathlib import Path
from queue import Queue
import time

import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice

from core.utils import StoppableThread, Buffer


class TTSThread(StoppableThread):
    def __init__(self, text: str, model) -> None:
        super().__init__()
        self._text = text
        self._model = model

    def callback(self, outdata, frames, time, status):
        if status:
            print("status:", status)

        if self._out_buf.is_empty():
            raise sd.CallbackStop()

        data = self._out_buf.get(frames)
        data = data.reshape(data.size, 1)
        outdata[:] = data

    def run(self):
        sd.default.samplerate = self._model.config.sample_rate
        sd.default.device = 'pulse'
        sd.default.channels = 1
        sd.default.blocksize = 1280
        sd.default.dtype = "int16"

        self._out_buf = Buffer()

        with sd.OutputStream(callback=self.callback) as stream:

            print("Speak:", self._text)

            for chunk in self._model.synthesize_stream_raw(self._text):
                if self.is_stopped():
                    print("Stream interrupted")
                    break

                self._out_buf.put(np.frombuffer(chunk, dtype=np.int16))

            while stream.active and not self.is_stopped():
                time.sleep(.1)

        self.stop()


class TTS():
    def __init__(self, model_path: Path):
        if not model_path.is_file():
            raise FileNotFoundError(f"TTS model file doesn't exist, {model_path}")

        self._model = PiperVoice.load(model_path)

    def __call__(self, text: str):
        self._text = text
        return self

    def __enter__(self):
        self._t = TTSThread(self._text, self._model)
        self._t.start()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._t.stop()
        self._t.join()

    def speak(self, text: str):
        """ Blocking speak """
        with self(text):
            self.wait()

    def is_speaking(self):
        return not self._t.is_stopped()

    def wait(self, interrupt_cb=None):
        """ If interrupt cb is provided, method will return True if interrupted """
        while self.is_speaking():
            if interrupt_cb and interrupt_cb():
                return True
            time.sleep(.1)
