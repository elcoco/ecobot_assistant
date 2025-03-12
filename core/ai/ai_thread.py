from queue import Queue
from typing import Optional

from ollama import Client

from core.utils import StoppableThread

from core.ai.tools.base import ToolBaseClass, ToolError
from core.ai import model


class AIThread(StoppableThread):
    def __init__(self, query, history: list[dict], tools: Optional[list[ToolBaseClass]]=None, host: str="127.0.0.1", port: int=11434) -> None:
        super().__init__()
        self._q = Queue()
        self._query = query

        # Keep a history of messages
        self._history = history

        self._tools = tools or []
        self._client = Client(host=f"{host}:{port}")

    def find_tool(self, tools, name):
        return next((t for t in tools if t.name == name), None)

    def is_sentence(self, buf: str):
        endings = [".\n", ". ", ":\n", "? ", "?\n", "! ", "!\n"]
        return any([buf[-2:] == x for x in endings])

    def sanitize(self, buf: str):
        return buf.replace("\n", "")

    def call(self, query: str, history=None):
        msg = {"role": "user", "content": query}

        if history:
            history.append(msg)
            messages = history
        else:
            messages = [msg]

        sentence_buf = ""
        response = ""
        print(messages)

        stream = self._client.chat( model=model,
                                    messages=messages,
                                    stream = True )
        for chunk in stream:
            if self.is_stopped():
                break

            for c in chunk.message.content:
                sentence_buf += c
                if self.is_sentence(sentence_buf):
                    #print("queue:", self.sanitize(sentence_buf))
                    self._q.put(self.sanitize(sentence_buf))
                    response += (". " + self.sanitize(sentence_buf))
                    sentence_buf = ""

            # put last bit in list before exit
            if chunk.done:
                if sentence_buf:
                    self._q.put(sentence_buf)
                    response += (". " + self.sanitize(sentence_buf))
                break

        if history:
            history.append({"role": "assistant", "content": response})
        self.stop()
        print("exit")

    def call_tools(self, query: str, tools: list[ToolBaseClass]):
        for tool in tools:
            return tool.call(query)

    def has_data(self):
        return not self._q.empty()

    def get_sentence(self):
        return self._q.get()

    def run(self):
        """ Finds sentences in ai output and puts them in queue """
        print("Lookup AI")

        tools_filtered = [t for t in self._tools if t._pattern and t.pre_match(self._query)]
        if tools_filtered:
            result = self.call_tools(self._query, tools_filtered)
            self._q.put(result)
        else:
            self.call(self._query)

        self.stop()
        #self.call(self._query, self._history)
