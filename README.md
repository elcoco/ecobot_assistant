# ecobot_assistant

## Install in virtual env

### Install piper-tts

    # requires python 3.12.x
    pip install piper-tts --no-deps piper-phonemize-cross onnxruntime numpy

### Install openwakeword
Archlinux won't allow direct install of openwakeword because tflite-runtime package in uninstallable.  
By cloning the repo and commenting out the tflite dependency we can install the package in the venv.  

    git clone https://github.com/dscripka/openWakeWord
    vi openwakeword/setup.py
    pip install -e openwakeword

#### Install openwakeword models

    import openwakeword
    openwakeword.utils.download_models()
