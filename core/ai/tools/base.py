from typing import Optional
import re


class ToolError(Exception):
    ...

class ToolBaseClass():
    def __init__(self, cfg: dict, pre_match: Optional[str]=None, skip_ai: bool=False, ai_client=False, ai_model: Optional[str]=None):
        self._config = cfg

        # Pre match checks request against given reggex
        if pre_match:
            self._pattern = re.compile(pre_match)
        else:
            self._pattern = None

        # Indicate if it is needed to let ai parse query into parameters.
        # eg. some calls like "stop playing" or "pause playing" don't need any arguments and
        # skipping ai parsing makes the process a lot faster
        self.skip_ai = skip_ai

        # Pointer to ai object
        self._ai_client = ai_client
        self._ai_model = ai_model

    def call_ai_tools(self, query: str) -> dict:
        """ Call ai and parse query into arguments """
        response = self._ai_client.chat(model=self._ai_model,
                                   messages=[{"role": "user", "content": query}],
                                   tools=[self.get_cfg()],
                                   )

        print(response)
        if response.message.tool_calls:

            tc = response.message.tool_calls[0]
            if tc.function.name != self.name:
                raise ToolError("No suitable tools found!")

            return tc.function.arguments

        elif response.message.content:
            raise ToolError(response.message.content)

        raise ToolError(f"No tools found for query")


    @property
    def name(self):
        return self._config["function"]["name"]

    def get_cfg(self):
        return self._config

    def call(self, *args, **kwargs):
        """ Needs to be implemented when subclassing """

    def pre_match(self, text):
        """ Check patern against the query so that we can see what tool to use """
        if self._pattern:
            return re.match(self._pattern, text)

        return True
