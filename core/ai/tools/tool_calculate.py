import operator

from core.ai.tools.base import ToolBaseClass, ToolError


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
        super().__init__(cfg, *args, pre_match=r"^calculate", **kwargs)

    def calc(self, op: str, n0: float, n1: float):
        match op:
            case "+":
                return operator.add(n0, n1)
            case "-":
                return operator.sub(n0, n1)
            case "*":
                return operator.mul(n0, n1)
            case "/":
                return operator.truediv(n0, n1)
            case "^":
                return operator.pow(n0, n1)
            case _:
                return "Unsupported operator"

    def call(self, n0: str, n1: str, op: str) -> str:
        try:
            left = float(n0)
            right = float(n1)
        except ValueError:
            raise ToolError(f"{self.name}: Argument error, args: {n0}, {op}, {n1}")

        return f"{n0} {op} {n1} is {self.calc(op, left, right)}"

