from queue import Queue
import numpy as np
from pathlib import Path
import time


import sounddevice as sd
from piper.voice import PiperVoice
from openwakeword.model import Model

from core.utils import Buffer



in_q = Queue()
out_q = Queue()
out_buf = Buffer()

tts_model = Path("assets/tts_models/en_US-amy-low.onnx")

ww_inference_fw = "onnx"
ww_model_path = Path("assets/ww_models/hey_jarvis_v0.1.onnx")
ww_model_name = "hey_jarvis_v0.1"

owwModel = Model(wakeword_models=[str(ww_model_path)], inference_framework=ww_inference_fw)

voice = PiperVoice.load(tts_model)


sd.default.samplerate = 16000
sd.default.device = 'pulse'
sd.default.channels = 1
sd.default.blocksize = 1280
sd.default.dtype = "int16"


def callback(in_data, outdata, frames, time, status):
    if status:
        print(status)

    in_q.put(np.frombuffer(in_data, dtype=np.int16))
    #in_q.put(in_data.copy())

    if out_buf.is_empty():
        print("exit cb")
        raise sd.CallbackStop()

    data = out_buf.get(frames)
    data = data.reshape(data.size, 1)
    outdata[:] = data



def is_triggered(frame, treshold=.6):
    """ Feed frame and check if there is a wakeword """

    if not len(frame):
        print("no input")
        return


    print("ww framelen:", len(frame))

    # Feed to openWakeWord model
    prediction = owwModel.predict(frame)

    scores = list(owwModel.prediction_buffer[ww_model_name])
    print("SCORE:", scores[-1])

    if score := scores[-1] > treshold:
        print("SCORE:", scores[-1])
        return score

def speak_ww(text, ww_cb):
    # TODO: listen to wakeword while playing and stop if encountered
    print("sr:", voice.config.sample_rate)
    #sr = 22050
    #sd.default.samplerate = voice.config.sample_rate

    with sd.Stream(callback=callback) as stream:

        print("SPEAK:", text)
        result = True

        for chunk in voice.synthesize_stream_raw(text):

            print("Checking ww")
            while not in_q.empty():
                if ww_cb(in_q.get()):
                    print("!!!!!!!!!!!!!!!!!!!1 wakeword detected")
                    break

            out_buf.put(np.frombuffer(chunk, dtype=np.int16))

        while stream.active:
            while not in_q.empty():
                if ww_cb(in_q.get()):
                    print("!!!!!!!!!!!!!!!!!!!1 wakeword detected")
                    break

    print("exit")
    return result


text = """Example text, often referred to as placeholder text, is commonly used in graphic design, publishing, and web development to fill empty spaces
Example text, often referred to as placeholder text, is commonly used in graphic design, publishing, and web development to fill empty spaces
"""
speak_ww(text, is_triggered)

