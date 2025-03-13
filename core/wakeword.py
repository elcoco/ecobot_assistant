from pathlib import Path
import time
from queue import Queue

import sounddevice as sd
import numpy as np
from openwakeword.model import Model

from core.utils import StoppableThread


class WWThread(StoppableThread):
    def __init__(self, model, model_name):
        super().__init__()
        self._chunk_size = 1280
        self._model = model
        self._model_name = model_name
        self._treshold = .60

        sd.default.samplerate = 16000
        sd.default.device = 'pulse'
        sd.default.channels = 1

        self._stopped = False

    def is_triggered(self, frame):
        """ Feed frame and check if there is a wakeword """

        # Feed to openWakeWord model
        prediction = self._model.predict(frame)

        scores = list(self._model.prediction_buffer[self._model_name])

        if score := scores[-1] > self._treshold:
            print("Wakeword detected")
            self.stop()
            return score

    def run(self):
        with sd.Stream(dtype='int16') as stream:

            while not self.is_stopped():

                in_data, overflowed = stream.read(self._chunk_size)
                frame = np.frombuffer(in_data, dtype=np.int16)

                if self.is_triggered(frame):
                    break


class WakeWord():
    def __init__(self, model_path: Path, model_name):

        self._model_name = model_name
        self._model_path = model_path
        self._inference_fw = "onnx"

        if not self._model_path.is_file():
            raise FileNotFoundError(f"Wakeword model file doesn't exist, {self._model_path}")

        # Load pre-trained openwakeword models

    def __enter__(self):
        self._model = Model(wakeword_models=[str(self._model_path)], inference_framework=self._inference_fw)
        self._t = WWThread(self._model, self._model_name)
        self._t.start()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._t.stop()
        self._t.join()

    def is_triggered(self):
        return self._t.is_stopped()

    def stop(self):
        self._t.stop()
        self._t.join()

    def wait(self):
        with self:
            while not self.is_triggered():
                time.sleep(0.1)
