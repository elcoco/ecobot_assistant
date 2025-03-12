from ollama import Client

from core.ai.tools.base import ToolBaseClass, ToolError
from core.ai.tools.tool_calculate import CalcTool
from core.ai.tools.tool_convert import ConvertTool
from core.ai.tools.tool_music import MusicTool, MediaControlTool
from core.ai.tools.tool_timer import TimerTool
from core.ai.tools.tool_lookup import LookupNewsTool

tools: list[ToolBaseClass] = [ MusicTool(),
                               MediaControlTool(),
                               CalcTool(),
                               ConvertTool(),
                               TimerTool(),
                               LookupNewsTool() ]



host = "localhost"
port = 11434
model = "llama3.2"
