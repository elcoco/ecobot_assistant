from typing import Optional
from pprint import pprint
import json
import operator

from core.ai.ai_thread import AIThread


class AI():
    def __init__(self) -> None:
        self._history = []

    def __call__(self, query: str, tools):
        self._query = query
        self._tools = tools
        return self

    def __enter__(self):
        self._t = AIThread(self._query, self._history, self._tools)
        self._t.start()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._t.stop()
        self._t.join()

    def clear_history(self):
        """ Clear history and start fresh on next query. """
        self._history = []

    def get_sentence(self):
        return self._t.get_sentence()

    def has_data(self):
        return self._t.has_data()

    def is_finished(self):
        return self._t.is_stopped() and not self.has_data()

