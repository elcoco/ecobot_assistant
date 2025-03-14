from pathlib import Path

from core.wakeword import WakeWord
from core.tts import TTS
from core.stt import STT


stt = STT(Path("assets/stt_models/vosk-model-small-en-us-0.15"))
tts = TTS(Path("assets/tts_models/en_US-lessac-medium.onnx"))
ww = WakeWord(Path("assets/ww_models/hey_jarvis_v0.1.onnx"), "hey_jarvis_v0.1")


from core.ai.tools.tool_calculate import CalcTool
from core.ai.tools.tool_convert import ConvertTool
from core.ai.tools.base import ToolBaseClass
from core.ai.tools.tool_music import MusicTool, MediaControlTool
from core.ai.tools.tool_timer import TimerTool
from core.ai.tools.tool_lookup import LookupNewsTool
from core.ai.tools.tool_kodi import KodiTool
from core.ai.tools.tool_conversation import ConversationTool

#ai_model = "llama3.2:1b"
#ai_model = "phi4-mini"
ai_model = "llama3.2"

tools: list[ToolBaseClass] = [ LookupNewsTool(ai_model),
                               MediaControlTool(ai_model),
                               ConvertTool(ai_model),
                               CalcTool(ai_model),
                               ConversationTool(ai_model),
                               KodiTool(ai_model, host="http://192.168.178.248:8080/jsonrpc"),
                               TimerTool(ai_model) ]
