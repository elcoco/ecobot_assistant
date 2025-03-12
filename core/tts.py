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
        # TODO: listen to wakeword while playing and stop if encountered
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
                #if interrupt_cb and interrupt_cb():
                #    print("Stream interrupted by wakeword")
                #    break

            while stream.active and not self.is_stopped():
                #if interrupt_cb and interrupt_cb():
                #    print("Stream interrupted by wakeword")
                #    break

                time.sleep(.1)

            #print("Stream ended")
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

    def is_speaking(self):
        return not self._t.is_stopped()

    def wait(self):
        while self.is_speaking():
            time.sleep(.1)
