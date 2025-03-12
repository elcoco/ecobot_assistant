import sys
import queue
from pathlib import Path
import json
import time

import vosk
import sounddevice as sd


class STT():
    def __init__(self, model_path: Path, timeout=2):
        #self._model_path = Path("assets/stt_models/vosk-model-en-us-0.22")
        self._model_path = model_path
        self._sample_rate = 44100
        self._block_size = 8000

        if not self._model_path.is_dir():
            raise FileNotFoundError(f"STT model file doesn't exist, {self._model_path}")

        self._q = queue.Queue()

        self._silence_treshold_sec = timeout
        self._model = vosk.Model(str(self._model_path))

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self._q.put(bytes(indata))

    def get_timestamp(self):
        return time.time()

    def listen(self):

        t_last = None
        result = []

        print("Listening...")

        sd.default.samplerate = self._sample_rate
        sd.default.device = 'pulse'
        sd.default.channels = 1
        sd.default.blocksize = self._block_size
        sd.default.dtype = "int16"

        with sd.RawInputStream(callback=self.callback):

            rec = vosk.KaldiRecognizer(self._model, self._sample_rate)
            while True:
                data = self._q.get()

                # NOTE: AcceptWaveform returns True when silence (EOL) is detected
                if rec.AcceptWaveform(data):
                    result.append(json.loads(rec.Result())["text"])
                    print("\ntext:", result)
                    t_last = self.get_timestamp()
                elif partial := json.loads(rec.PartialResult())["partial"]:
                    print("\rpartial:", partial, end="")
                elif t_last:
                    if self.get_timestamp() - t_last > self._silence_treshold_sec:
                        print("Timedout:", self.get_timestamp() - t_last)
                        break

            return result
