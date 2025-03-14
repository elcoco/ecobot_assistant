import operator

from core.ai.tools.base import ToolBaseClass, ToolError
from core import tts, stt, ww

op_map = {
    "+": "plus",
    "-": "minus",
    "*": "times",
    "/": "divided by",
    "^": "to the power of",
}

op_map_reversed = {
    "multiply": "*",
    "times": "*",
}

class CalcTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "calculation",
                "description": "make a calculation with 2 numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n0": {"type": "float", "description": "the first number" },
                        "n1":   {"type": "float", "description": "the second number" },
                        "op": {"type": "string", "description": "the operator" },
                    },
                    "required": ["n0", "op", "n1"],
                },
            }
        }
        super().__init__(cfg, r"^calculate", *args, **kwargs)

    def calc(self, n0: str, n1: str, op: str) -> str:
        try:
            left = float(n0)
            right = float(n1)
        except ValueError:
            tts.speak("Got weird arguments")
            raise ToolError(f"{self.name}: Argument error, args: {n0}, {op}, {n1}")

        op = op_map_reversed.get(op, op)

        match op:
            case "+":
                result = operator.add(left, right)
            case "-":
                result = operator.sub(left, right)
            case "*":
                result = operator.mul(left, right)
            case "/":
                result = operator.truediv(left, right)
            case "^":
                result = operator.pow(left, right)
            case _:
                return "Unsupported operator"

        return f"{n0} {op_map[op]} {n1} is {result}"

    def call(self, query: str):
        if not (args := self.parse_args(query, ww, tts)):
            return

        tts.speak(self.calc(**args))
