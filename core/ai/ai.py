from typing import Optional
from pprint import pprint
import time

from core.ai.ai_thread import AIToolThread, AIThread

def pre_match_tools(tools, query: str):
    return iter([tool for tool in tools if tool._pattern and tool.pre_match(query)])


class AI():
    """ A context wrapper that manages the ai thread. """
    def __init__(self, model: str) -> None:
        self._context = None
        self._model = model
        self._tools = None

    def __call__(self, query: str, context: Optional[list]=None, tools: Optional[list]=None):
        self._query = query
        self._tools = tools
        self._context = context
        return self

    def __enter__(self):

        if self._tools:
            print("running tools")
            self._t = AIToolThread(self._query, self._model, self._context, self._tools)
        else:
            print("running without tools")
            self._t = AIThread(self._query, self._model, self._context)

        self._t.start()
        return self._t

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._t.stop()
        self._t.join()

    def clear_history(self):
        """ Clear history and start fresh on next query. """
        self._history = []

    def wait(self):
        while not self._t.is_finished():
            time.sleep(.1)
