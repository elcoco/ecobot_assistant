from queue import Queue
from typing import Optional

from ollama import Client

from core.utils import StoppableThread


class AIThreadBaseClass(StoppableThread):
    def __init__(self, query: str, model: str, context: list[dict], tools: Optional[list]=None, host: str="127.0.0.1", port: int=11434) -> None:
        super().__init__()
        self._q = Queue()
        self._query = query
        self._model = model

        # Keep a context of messages
        self._context = context

        self._tools = tools or []
        self._client = Client(host=f"{host}:{port}")

    def find_tool(self, tools, name):
        return next((t for t in tools if t.name == name), None)

    def is_sentence(self, buf: str):
        endings = [".\n", ". ", ":\n", "? ", "?\n", "! ", "!\n"]
        return any([buf[-2:] == x for x in endings])

    def sanitize(self, buf: str):
        return buf.replace("\n", "")

    def has_data(self):
        return not self._q.empty()

    def is_finished(self):
        return self.is_stopped() and not self.has_data()

    def get_sentence(self):
        return self._q.get()

    def run(self):
        """ Finds sentences in ai output and puts them in queue """


class AIThread(AIThreadBaseClass):
    def __init__(self, *args, fmt: Optional[dict]=None, **kvargs):
        super().__init__(*args, **kvargs)

        # The format specifies the used layout of a json file that needs to be parsed by the ai
        self._fmt = fmt

    def call(self, query: str, context=None):
        msg = {"role": "user", "content": query}

        if context:
            context.append(msg)
            messages = context
        else:
            messages = [msg]

        sentence_buf = ""
        response = ""
        print(messages)

        stream = self._client.chat( model=self._model,
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

        if context:
            context.append({"role": "assistant", "content": response})
        self.stop()
        print("exit")

    def run(self):
        print("Lookup AI")

        self.call(self._query, self._context)
        self.stop()


class AIToolThread(AIThreadBaseClass):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self._args = {}

    def call(self, query: str, tools: list):
        """ Call ai and parse query into arguments """
        response = self._client.chat(model=self._model,
                                   messages=[{"role": "user", "content": query}],
                                   tools=tools )

        print(response)
        if response.message.tool_calls:

            # only handle fi9rst match
            tc = response.message.tool_calls[0]

            self._args = tc.function.arguments
            return

        elif response.message.content:
            self._q.put(response.message.content)
            return

        self._q.put(f"No tools found for query")

    def get_args(self):
        return self._args

    def run(self):
        self.call(self._query, self._tools)
        self.stop()

